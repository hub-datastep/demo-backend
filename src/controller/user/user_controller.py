from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from dto.user_dto import UserDto
from infra.database import get_session
from repository import user_repository
from scheme.user_scheme import UserCreate, UserRead
# from service.auth_service import AuthService

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.post("", response_model=UserRead)
@version(1)
def create_user(*, session: Session = Depends(get_session), user: UserCreate):
    return user_repository.create_user(session, user)


@router.post("/{user_id}", response_model=UserRead)
@version(1)
def get_user_by_id(*, session: Session = Depends(get_session), user_id: int):
    return user_repository.get_user_by_id(session, user_id)

# @router.get("/current")
# @version(1)
# def get_current_user(current_user: UserDto = Depends(AuthService.get_current_user)):
#     return current_user
