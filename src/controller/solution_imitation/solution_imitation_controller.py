from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth.auth_model import get_current_user
from model.solution_imitation import solution_imitation_model
from scheme.user.user_scheme import UserRead
from src.scheme.solution_imitation.solution_imitation_scheme import (
    SolutionImitationRequest,
)

router = APIRouter()


@router.post(
    "/with_llm",
    # response_model=,
)
@version(1)
def imitate_solution_with_llm(
    file_object: UploadFile,
    body: SolutionImitationRequest,
    session: Session = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return solution_imitation_model.imitate_solution(
        session=session,
        current_user=current_user,
        file_object=file_object,
        body=body,
    )
