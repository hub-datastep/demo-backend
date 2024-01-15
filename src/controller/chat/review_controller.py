from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from repository import review_repository
from scheme.review_scheme import ReviewCreate, ReviewRead

router = APIRouter(
    prefix="/review"
)


@router.post("", response_model=ReviewRead)
@version(1)
def create_review(*, session: Session = Depends(get_session), review: ReviewCreate):
    return review_repository.create_review(session, review)
