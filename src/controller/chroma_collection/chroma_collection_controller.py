from fastapi import APIRouter, Depends
from fastapi_versioning import version

from infra import chroma_store
from middleware.role_middleware import admins_only
from model.auth.auth_model import get_current_user
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("/list", response_model=list[str])
@version(1)
@admins_only
def get_all_chroma_collections(
    current_user: UserRead = Depends(get_current_user),
):
    """
    Получает список всех названий коллекций.
    """
    return chroma_store.get_all_collections()


@router.get("/{collection_name}/length")
@version(1)
@admins_only
def get_chroma_collection_length(
    collection_name: str,
    current_user: UserRead = Depends(get_current_user),
) -> int:
    """
    Получает количество векторов в Chroma коллекции.
    """
    return chroma_store.get_collection_length(collection_name=collection_name)


@router.post("/{collection_name}")
@version(1)
@admins_only
def create_chroma_collection(
    collection_name: str,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Создает Chroma коллекцию.
    """
    return chroma_store.create_collection(collection_name=collection_name)


@router.delete("/{collection_name}")
@version(1)
@admins_only
def delete_chroma_collection(
    collection_name: str,
    current_user: UserRead = Depends(get_current_user),
):
    """
    Удаляет Chroma коллекцию.
    """
    return chroma_store.delete_collection(collection_name=collection_name)
