from config.config import config
from datastep.components.chain import get_llm
from datastep.components.questions.question_chain_executor import get_question_chain_executor

question_service = get_question_chain_executor(
    get_llm(model_name="gpt-4"),
    debug=True,
    verbose_answer=config["verbose_answer"]
)
