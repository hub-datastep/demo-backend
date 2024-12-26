from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth.auth_model import get_current_user
from model.solution_imitation import solution_imitation_model
from scheme.solution_imitation.solution_imitation_llm_output_scheme import LLMOutput
from scheme.user.user_scheme import UserRead
from scheme.solution_imitation.solution_imitation_scheme import (
    SolutionImitationRequest,
)

router = APIRouter()


@router.post(
    "/with_llm/{type}",
    # response_model=list[LLMOutputTable],
    response_model=LLMOutput,
)
@version(1)
def imitate_solution_with_llm(
    file_object: UploadFile,
    # TODO: try to fix body with UploadFile
    # body: SolutionImitationRequest,
    type: str,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    body = SolutionImitationRequest(type=type)
    return solution_imitation_model.imitate_solution(
        session=session,
        current_user=current_user,
        file_object=file_object,
        body=body,
    )
