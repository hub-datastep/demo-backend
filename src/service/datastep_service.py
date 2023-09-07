from config.config import config
from datastep.components.chain import get_db, get_llm
from datastep.components.sql_database_chain_executor import get_sql_database_chain_executor
from dto.prompt_out_dto import PromptOutDto
from repository.prompt_repository import prompt_repository

prompt_dto: PromptOutDto = prompt_repository.fetch()

datastep_service = get_sql_database_chain_executor(
    get_db(),
    get_llm(model_name="gpt-3.5-turbo-16k"),
    debug=True,
    verbose_answer=config["verbose_answer"]
)
