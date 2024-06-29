from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth.auth_model import get_current_user
from repository import review_repository
from scheme.chat.review_scheme import ReviewCreate, ReviewRead
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.post("", response_model=ReviewRead)
@version(1)
def create_review(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session),
    review: ReviewCreate
):
    """
    """
    return review_repository.create_review(session, review)
