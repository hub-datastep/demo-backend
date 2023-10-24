from fastapi import APIRouter
from fastapi_versioning import version

from model import tenant_logo_model

router = APIRouter(
    prefix="/logo",
    tags=["logo"],
)


@router.get("/{user_id}")
@version(1)
def get_logo_by_tenant_id(user_id: str):
    return tenant_logo_model.get_logo(user_id)
