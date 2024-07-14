from fastapi import APIRouter
from fastapi import Depends
from fastapi_versioning import version

from model.ksr.ksr_api_model import get_ksr

router = APIRouter()


@router.get("", response_model=dict)
@version(1)
def get_ksr_by_id(id_ksr: str) -> dict:
    return get_ksr(id_ksr)
