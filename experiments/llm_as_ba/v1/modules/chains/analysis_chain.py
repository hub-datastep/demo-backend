import time
from typing import Optional, Dict, Any
import traceback

from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from loguru import logger
from openai import RateLimitError

from llm_as_ba.v1.modules.constants import (
    WAIT_TIME_IN_SEC,
    SCENARIO_TYPE_QA,
    SCENARIO_TYPE_ACTION,
    REQUEST_ID_FIELD,
    REQUEST_CONTENT_FIELD,
    SERVICE_FIELD,
    EXECUTOR_COMMENT_FIELD,
    CHAT_HISTORY_FIELD,
)
from llm_as_ba.v1.modules.schemas import Intent, Scenario, RequestAnalysis, KnowledgeBase, KnowledgeBaseEntry, AnalysisResponse


_PROMPT_TEMPLATE = """
Ты - аналитик обращений жителей в управляющую компанию. Твоя задача - проанализировать обращение жителя + заявку и определить:
1. Интент (намерение жителя)
2. Место формулировки интента
3. Тип сценария обработки обращения
4. Сценарий обработки обращения


Информация о заявке:

Услуга:
```
{service}
```

Суть обращения:
```
{request_content}
```

Комментарий исполнителя:
```
{executor_comment}
```

Чат по заявке:
```
{chat_history}
```

Проведи полный анализ обращения:

1. Определи основное намерение (интент) жителя. Интент - это то, чего хочет добиться житель своим обращением или другими словами - почему он решил обратиться.
2. Также укажи, где была сформулирована суть интента: в содержании заявки, в чате или в обоих источниках.

3. Определи сценарий обработки обращения. Сценарий это то что происходит для того чтобы помочь жителю. Для доп информации тебе - существует два типа сценариев:
   - actionless_qa: достаточно просто ответить на вопрос жителя без выполнения каких-либо действий.
   - action_required: необходимо выполнить определенные действия для решения проблемы жителя (например, вызвать инженера или изменить данные в системе).
   Тебе нужно описать сценарий который произошел после прихода заявки. Это может быть как и просто ответ на вопрос жителя, так и действия типа "вызов главного инженера". Если не понятно что сделал исполнитель - просто оставь пустоту

4. Определи тип сценария обработки этого обращения. Существует два типа сценариев:
   - actionless_qa: достаточно просто ответить на вопрос жителя без выполнения каких-либо действий.
   - action_required: необходимо выполнить определенные действия для решения проблемы жителя (например, вызвать инженера или изменить данные в системе).


Интент формулируй в идеале несколькими словами, максимум одно предложение
Пример 1:
- правильный интент: "Узнать причину регулярной отмены пропуска на машину"
- неправильный интент: "Житель хочет узнать причину регулярной отмены пропуска на машину и получить обратную связь по этому вопросу."

Пример 2:
- правильный интент: Житель хочет получить информацию о том, почему показания счетчика отопления не передаются автоматически и как это исправить.
- неправильный интент: Узнать почему показания счетчика отопления не передаются автоматически через приложение

Ответь в формате JSON по схеме:
{format_instructions}
"""


def _get_analysis_prompt() -> tuple:
    parser = JsonOutputParser(pydantic_object=AnalysisResponse)
    
    prompt = PromptTemplate(
        input_variables=[
            "service",
            "request_content",
            "executor_comment",
            "chat_history"
        ],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        template=_PROMPT_TEMPLATE,
    )
    return prompt, parser


def get_analysis_chain(
    llm: AzureChatOpenAI,
    verbose: bool = False,
) -> tuple:
    prompt, parser = _get_analysis_prompt()

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=verbose,
    )
    return chain, parser


def analyze_request(
    llm: AzureChatOpenAI,
    request_id: str,
    request_content: str,
    service: str = "",
    executor_comment: str = "",
    chat_history: Optional[str] = None,
    verbose: bool = False,
) -> RequestAnalysis:
    """Analyze a resident request to determine intent, scenario, and knowledge base categorization in one call."""
    try:
        chain, parser = get_analysis_chain(
            llm=llm,
            verbose=verbose,
        )

        # Set default values for empty inputs
        if not service:
            service = "Не указана"
        if not executor_comment:
            executor_comment = "Отсутствует"
        if not chat_history:
            chat_history = "Чат отсутствует"

        # Run the chain
        analysis_response: str = chain.run(
            service=service,
            request_content=request_content,
            executor_comment=executor_comment,
            chat_history=chat_history,
        )
        
        # Parse the response using the JsonOutputParser
        parsed_response = parser.parse(analysis_response)
        # парсер ленгчейна после парсинга не приводит к схеме и на выходе получаем дикт 
        parsed_response = AnalysisResponse(**parsed_response)
        
        # Validate scenario type
        scenario_type = parsed_response.scenario_type
        if scenario_type not in [SCENARIO_TYPE_QA, SCENARIO_TYPE_ACTION]:
            if "actionless" in scenario_type.lower() or "qa" in scenario_type.lower():
                scenario_type = SCENARIO_TYPE_QA
            else:
                scenario_type = SCENARIO_TYPE_ACTION
        
        # Create the full analysis result
        result = {
            "request_id": request_id,
            "intent": Intent(
                intent_text=parsed_response.intent_text,
                intent_source=parsed_response.intent_source,
            ),
            "scenario": Scenario(
                scenario_type=parsed_response.scenario_type,
                description=parsed_response.scenario_details,
            ),
        }
        
        return RequestAnalysis(
            request_id=result["request_id"],
            intent=result["intent"],
            scenario=result["scenario"],
        )

    except RateLimitError as e:
        logger.error(f"RateLimit error occurred: {str(e)}")
        logger.info(f"Wait {WAIT_TIME_IN_SEC} seconds and try again")
        time.sleep(WAIT_TIME_IN_SEC)
        logger.info(
            f"Timeout passed, "
            f"try to analyze request '{request_id}' again"
        )

        return analyze_request(
            llm=llm,
            request_id=request_id,
            request_content=request_content,
            service=service,
            executor_comment=executor_comment,
            chat_history=chat_history,
            verbose=verbose,
        )
    except Exception as e:
        logger.error(f"Error getting LLM response: {str(e)}")
        logger.error(f"Raw response: {analysis_response}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        
        # Fallback to default values if parsing fails
        result = {
            "request_id": request_id,
            "intent": Intent(
                intent_text=f"Не удалось определить интент: {request_content[:50]}...",
                intent_source="неопределен",
            ),
            "scenario": Scenario(
                scenario_type=SCENARIO_TYPE_QA,
                description="Не удалось определить сценарий",
            ),
        }
        
        return RequestAnalysis(
            request_id=result["request_id"],
            intent=result["intent"],
            scenario=result["scenario"],
        )



def create_request_analysis(analysis_result: Dict[str, Any]) -> RequestAnalysis:
    """Create a RequestAnalysis object from the analysis result."""
    return RequestAnalysis(
        request_id=analysis_result["request_id"],
        intent=analysis_result["intent"],
        scenario=analysis_result["scenario"],
    )


def update_knowledge_base(
    knowledge_base: KnowledgeBase,
    analysis_result: RequestAnalysis,
    original_request: Dict[str, Any],
) -> KnowledgeBase:
    """Update the knowledge base with a new analysis result."""
    # Extract initial request data
    request_id = original_request.get(REQUEST_ID_FIELD, "")
    request_content = original_request.get(REQUEST_CONTENT_FIELD, "")
    service = original_request.get(SERVICE_FIELD, "")
    executor_comment = original_request.get(EXECUTOR_COMMENT_FIELD, "")
    chat_history = original_request.get(CHAT_HISTORY_FIELD, "")
    
    if isinstance(chat_history, list):
        chat_history = "\n".join(chat_history)
    
    
    # Create a new entry for each analyzed request
    new_entry = KnowledgeBaseEntry(
        # Initial request data
        request_id=request_id,
        request_content=request_content,
        service=service,
        executor_comment=executor_comment,
        chat_history=chat_history,
        
        # LLM output data
        intent_text=analysis_result.intent.intent_text,
        intent_source=analysis_result.intent.intent_source,
        scenario_type=analysis_result.scenario.scenario_type,
        scenario_details=analysis_result.scenario.description,
    )
    
    knowledge_base.entries.append(new_entry)
    return knowledge_base 