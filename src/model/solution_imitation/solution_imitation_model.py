from fastapi import HTTPException, status, UploadFile
from sqlmodel import Session
from scheme.user.user_scheme import UserRead
from repository.solution_imitation.solution_imitation_config_repository import (
    get_config_by_type_and_user_id,
)
from datastep.chains.solution_imitation_chain import (
    get_solution_imitation_chain,
    get_solution_imitation_prompt,
)
from scheme.solution_imitation.solution_imitation_scheme import (
    SolutionImitationRequest,
)
from model.file import utd_file_model, spec_file_model


class SolutionType:
    UTD = "utd"
    SPEC = "spec"
    IFC = "ifc"


# TODO - поменять аутпут с list[str] на массив обеъктов с айдишниками и строками (айдишники нужны для упрощения работы LLM и вывода строк в таблицу)
# Так чтобы совпадало со схемой llm output
def parse_input_file(type: str, file_object: UploadFile) -> list[str] | None:
    parsing_model = None

    # Parse UTD file
    if type == SolutionType.UTD:
        parsing_model = utd_file_model

    # Parse Specification file
    elif type == SolutionType.SPEC:
        parsing_model = spec_file_model

    # Parse IFC file
    elif type == SolutionType.IFC:
        return

    # Check if can parse file
    if parsing_model is None:
        return None

    parsed_data = parsing_model.extract_noms(file_object)

    return parsed_data


def imitate_solution(
    session: Session,
    current_user: UserRead,
    file_object: UploadFile,
    body: SolutionImitationRequest,
):
    # Get Input Data from Input File
    solution_type = body.type
    parsed_data = parse_input_file(
        type=solution_type,
        file_object=file_object,
    )

    # LLM solution Config
    user_id = current_user.id
    config = get_config_by_type_and_user_id(
        session=session,
        type=solution_type,
        user_id=user_id,
    )
    is_config_exists = config is not None

    if not is_config_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config with type '{type}' for user with ID {user_id} not found",
        )

    config_id = config.id

    # Prompt for LLM
    prompt_template = config.prompt
    is_prompt_exists = prompt_template is not None

    if not is_prompt_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config with ID {config_id} does not contain prompt",
        )

    # Input Variable for LLM
    input_variables = config.input_variables
    is_input_variables_exist = input_variables is not None

    if not is_input_variables_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config with ID {config_id} does not contain input variables",
        )

    # Init LLM chain
    llm_prompt = get_solution_imitation_prompt(
        template=prompt_template,
        input_variables=input_variables,
    )
    chain = get_solution_imitation_chain(prompt=llm_prompt)
    response = chain.run(input_data=parsed_data, return_json=True)

    # TODO: set "JSON response only" for LLM - тут вроде сделал, осталось только вызов модели прописать
    # TODO: convert LLM response to needed format and return - конвертацию в нужный формат модель сама должна сделать

    # осторожно - не запутаться бы в версиях langchain
    # У нас стоит 1 версия, дока по струкрутрному аутпуту такая https://python.langchain.com/v0.1/docs/modules/model_io/output_parsers/types/json/
    # Думаю что когда была первая версия лэнгчейна в мире еще не было json мода, поэтому они написали свой парсер текста в виде json который отдавала модель тогда
    # Но после 2 версии langchain появилась прям в нем встроенная поддержка режимов работы LLM
    # Вот гайд https://medium.com/@harshitdy/how-to-get-only-json-response-from-any-llm-using-langchain-ed53bc2df50f
    # Я попробовал написать по этому гайду - ошибок нет + нужные свойства есть в классах - поэтому думаю может прокатить
    # 
    # Но по хорошему нам надо мигрировать на 2 или 3 версию langchain а то мы упираемся в базовый фукнционал LLM уже, когда весь мир дальше идет

    # осталось попробовать вернуть response :)

    return 
