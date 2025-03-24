import os
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd
from langchain_openai import AzureChatOpenAI
from loguru import logger
from tqdm import tqdm

# Настройка логгера
logger.remove()  # Удаляем стандартный обработчик
logger.add(
    sink=lambda msg: print(msg),
    level="DEBUG",
    format="<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>"
)

from llm_as_ba.v1.modules.chains.analysis_chain import (
    analyze_request,
    update_knowledge_base,
)
from llm_as_ba.v1.modules.env import env
from llm_as_ba.v1.modules.schemas import KnowledgeBase
from llm_as_ba.v1.modules.constants import (
    INPUT_FILE_PATH,
    OUTPUT_DIR_PATH,
    SHEET_NAME,
    VERBOSE,
    REQUEST_ID_FIELD,
    REQUEST_CONTENT_FIELD,
    SERVICE_FIELD,
    EXECUTOR_COMMENT_FIELD,
    CHAT_HISTORY_FIELD,
)

def setup_llm(temperature: float = 0.0) -> AzureChatOpenAI:
    """Set up the LLM for the experiment."""
    return AzureChatOpenAI(
        api_key=env.EXPERIMENTS_API_KEY,
        azure_deployment=env.EXPERIMENTS_MODEL_NAME,
        azure_endpoint=env.EXPERIMENTS_AZURE_ENDPOINT,
        temperature=temperature,
    )

def process_requests_and_return_kb(
    llm: AzureChatOpenAI,
    data: List[Dict[str, Any]],
    output_dir: str,
    verbose: bool = False,
) -> KnowledgeBase:
    """Process a list of resident requests and build a knowledge base."""
    # Initialize the knowledge base
    knowledge_base = KnowledgeBase()
    
    # Use tqdm for progress tracking
    for item in tqdm(
        data,
        desc="Analyzing requests",
        total=len(data),
        unit="request"
    ):
        request_id = item.get(REQUEST_ID_FIELD, "")
        request_content = item.get(REQUEST_CONTENT_FIELD, "")
        service = item.get(SERVICE_FIELD, "")
        executor_comment = item.get(EXECUTOR_COMMENT_FIELD, "")
        chat_history = item.get(CHAT_HISTORY_FIELD, "")
        
        # logger.debug("request_content", request_content)
        # logger.debug("service", service)
        # logger.debug("executor_comment", executor_comment)

        if isinstance(chat_history, list):
            chat_history = "\n".join(chat_history)
        
        # Анализируем заявку с помощью LLM
        analysis_result = analyze_request(
            llm=llm,
            request_id=request_id,
            request_content=request_content,
            service=service,
            executor_comment=executor_comment,
            chat_history=chat_history,
            verbose=verbose,
        )
        
        logger.debug(f"Item: {item}")
        
        # Update the knowledge base
        knowledge_base = update_knowledge_base(
            knowledge_base=knowledge_base,
            analysis_result=analysis_result,
            original_request=item,
        )
      
        # # Log details if verbose
        # if verbose:
        #     logger.debug(f"Request ID: {request_id}")
        #     logger.debug(f"Request Content: {request_content}")
        #     logger.debug(f"Intent: {analysis_result['intent'].intent_text}")
        #     logger.debug(f"Intent Source: {analysis_result["intent"].intent_source}")
        #     logger.debug(f"Scenario: {analysis_result['scenario'].scenario_type}")
    
    return knowledge_base


def run_analysis(
    input_file: str = INPUT_FILE_PATH,
    output_dir: str = OUTPUT_DIR_PATH,
    sheet_name: str = SHEET_NAME,
    verbose: bool = VERBOSE,
):
    """Main function to run the experiment."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data from Excel file
    logger.info(f"Loading data from {input_file}, sheet: {sheet_name}")
    df = pd.read_excel(input_file, sheet_name=sheet_name)
    
    # Convert DataFrame to list of dictionaries
    data = df.to_dict(orient='records')
    
    logger.info(f"Loaded {len(data)} requests from {input_file}")
    
    # Set up LLM
    llm = setup_llm()
    
    # Process requests
    knowledge_base = process_requests_and_return_kb(
        llm=llm,
        data=data,
        output_dir=output_dir,
        verbose=verbose,
    )
    
    # Get and save knowledge base summary - now includes all entries
    # summary = get_knowledge_base_entries(knowledge_base)

    # Create results DataFrame with all entries
    results_df = pd.DataFrame([
        {
            # Initial request data
            "request_id": entry.request_id,
            "request_content": entry.request_content,
            "service": entry.service,
            "executor_comment": entry.executor_comment,
            "chat_history": entry.chat_history,
            
            # LLM output data
            "intent_text": entry.intent_text,
            "intent_source": entry.intent_source,
            "scenario_type": entry.scenario_type,
            "scenario_details": entry.scenario_details,
        }
        for entry in knowledge_base.entries
    ])
    
    # Save knowledge base summary to Excel
    now = datetime.now().strftime("%d-%m-%Y %H-%M")
    kb_file_path = os.path.join(output_dir, f"Knowledge Base Summary {now}.xlsx")
    
    results_df.to_excel(
        kb_file_path,
        sheet_name="Knowledge Base",
        index=False,
    )

    logger.info(f"Experiment completed. Results saved to {output_dir}")
    logger.info(f"Knowledge base summary saved to {kb_file_path}")
    
    # Print summary
    logger.info("Sample entries from knowledge base:")
    for i, entry in enumerate(knowledge_base.entries[:5]):
        logger.info(
            f"{i+1}. Request ID: {entry.request_id} - Intent: {entry.intent_text} - "
            f"Scenario Type: {entry.scenario_type}"
        )


if __name__ == "__main__":
    # Запуск анализа с настройками из констант
    run_analysis() 