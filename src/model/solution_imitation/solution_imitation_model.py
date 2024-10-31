from fastapi import HTTPException, status, UploadFile
from sqlmodel import Session
from src.scheme.user.user_scheme import UserRead
from src.repository.solution_imitation.solution_imitation_config_repository import (
    get_config_by_type_and_user_id,
)
from src.datastep.chains.solution_imitation_chain import (
    get_solution_imitation_chain,
    get_solution_imitation_prompt,
)
from src.scheme.solution_imitation.solution_imitation_scheme import (
    SolutionImitationRequest,
)
from src.model.file import utd_file_model, spec_file_model


class SolutionType:
    UTD = "utd"
    SPEC = "spec"
    IFC = "ifc"


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

    # TODO: set "JSON response only" for LLM
    # TODO: convert LLM response to needed format and return

    return
