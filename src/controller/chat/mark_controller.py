from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from repository import mark_repository
from scheme.mark_scheme import MarkRead, MarkCreate

router = APIRouter(
    prefix="/mark"
)


@router.post("", response_model=MarkRead)
@version(1)
def create_or_update_mark(*, session: Session = Depends(get_session), mark: MarkCreate):
    return mark_repository.create_or_update_mark(session, mark)
