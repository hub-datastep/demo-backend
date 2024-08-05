from fastapi import APIRouter
from fastapi import Depends
from fastapi_versioning import version

from middleware.role_middleware import admins_only
from model.auth.auth_model import get_current_user
from model.ner.ner import ner_service
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("", response_model=str)
@version(1)
@admins_only
def get_ner_brand_results(
    nomenclature: str,
    current_user: UserRead = Depends(get_current_user),
) -> str:
    return ner_service.predict([nomenclature])[0]


@router.post("/all", response_model=list[str])
@version(1)
@admins_only
def get_all_ner_brand_results(
    nomenclatures_list: list[str],
    current_user: UserRead = Depends(get_current_user),
) -> list[str]:
    return ner_service.predict(nomenclatures_list)
