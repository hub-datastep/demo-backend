from fastapi import APIRouter
from fastapi_versioning import version

from middleware.role_middleware import admins_only
from model.ksr.ksr_api_model import get_ksr

router = APIRouter()


@router.get("", response_model=dict)
@version(1)
@admins_only
def get_ksr_by_id(id_ksr: str) -> dict:
    return get_ksr(id_ksr)
