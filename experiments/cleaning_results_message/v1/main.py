from datetime import datetime

from langchain_openai import AzureChatOpenAI
from loguru import logger
from pandas import read_excel
from tqdm import tqdm

from cleaning_results_message.v1.modules.chains.cleaning_result_message_chain import (
    get_cleaning_results_message,
    get_cleaning_results_message_chain,
)

from cleaning_results_message.v1.modules.env import env

llm = AzureChatOpenAI(
    azure_deployment=env.EXPERIMENTS_MODEL_NAME,
    api_key=env.EXPERIMENTS_API_KEY,
    azure_endpoint=env.EXPERIMENTS_AZURE_ENDPOINT,
    temperature=0,
    verbose=False,
)

chain = get_cleaning_results_message_chain(llm=llm)

if __name__ == "__main__":
    FILE_PATH = "/home/syrnnik/Downloads/vysota/cleaning-results-message-with-llm/LLM Message Tests.xlsx"
    SHEET_NAME = "test-cases"

    test_cases = read_excel(FILE_PATH, SHEET_NAME)

    test_cases["Сообщение от LLM"] = None
    test_cases["Пояснение к Сообщению"] = None
    test_cases["Отфильтрованный Коммент Исполнителя"] = None
    for i, case in tqdm(
        test_cases.iterrows(),
        desc="Generate Message",
        total=len(test_cases),
        unit="1 message",
    ):
        order_query = case["Жалоба Жильца"]
        order_query = order_query.replace("\n", " ").strip()
        order_status_comment = case["Комментарий Исполнителя"]
        order_status_comment = order_status_comment.replace("\n", " ").strip()

        response = get_cleaning_results_message(
            chain=chain,
            order_query=order_query,
            order_status_comment=order_status_comment,
        )
        case["Сообщение от LLM"] = response.message
        case["Пояснение к Сообщению"] = response.comment
        case["Отфильтрованный Коммент Исполнителя"] = response.filtered_comment

        test_cases.loc[i] = case

        logger.debug(f"Order Query:{order_query}")
        logger.debug(f"Order Status Comment:{order_status_comment}")
        logger.debug(f"LLM Response:\n{response}")

    now = datetime.now().strftime("%d-%m-%Y %H-%M")
    EXPORT_FILE_PATH = f"LLM Message Test Results {now}.xlsx"
    EXPORT_SHEET_NAME = f"Results from {now}"
    test_cases.to_excel(
        EXPORT_FILE_PATH,
        sheet_name=EXPORT_SHEET_NAME,
        index=False,
    )
