from fastapi import APIRouter, Depends
from fastapi_versioning import version
from sqlmodel import Session

from infra.database import get_session
from model.auth.auth_model import get_current_user
from repository import message_repository
from scheme.chat.message_scheme import MessageRead, MessageCreate
from scheme.user.user_scheme import UserRead


router = APIRouter()


@router.post("", response_model=MessageRead)
@version(1)
def create_message(
    *, 
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session), 
    message: MessageCreate
):
    """
    """
    return message_repository.create_message(session, message)


@router.delete("/{chat_id}")
@version(1)
def clear_all_messages_by_chat_id(
    *,
    current_user: UserRead = Depends(get_current_user),
    session: Session = Depends(get_session), 
    chat_id: int
):
    """
    """
    return message_repository.drop_all_messages_by_chat_id(session, chat_id)


# @router.get("/favorite/{user_id}")
# @version(1)
# def get_favorites_list_by_user_id(
#     *,
#     current_user: UserRead = Depends(get_current_user)
# ):
#     return message_repository.get_favorites_list(current_user.id)
# 
# 
# @router.post("/favorite")
# @version(1)
# def add_message_to_favorites_list(
#     *,
#     current_user: UserRead = Depends(get_current_user),
#     body: CreateFavoriteMessageDto
# ):
#     return message_repository.add_favorite_message(body)
# 
# 
# @router.delete("/favorite/{favorite_message_id}")
# @version(1)
# def remove_favorite_message(
#     *,
#     current_user: UserRead = Depends(get_current_user),
#     favorite_message_id: int
# ):
#     return message_repository.remove_favorite_message(favorite_message_id)
