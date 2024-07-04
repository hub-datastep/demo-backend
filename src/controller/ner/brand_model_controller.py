from fastapi import APIRouter
from fastapi import Depends
from fastapi_versioning import version

from model.auth.auth_model import get_current_user
from model.ner.brand_model import brand_ner_model
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("", response_model=str)
@version(1)
def get_ner_brand_results(
    text: str,
    current_user: UserRead = Depends(get_current_user),
) -> str:
    """
    Получает результат NER. На входе название номенклатуры, на выходе название компании производителя.
    """
    return brand_ner_model.get_ner_brand(text)

@router.get("/all", response_model=list[str])
@version(1)
def get_all_ner_brand_results(
    text: list[str],
    current_user: UserRead = Depends(get_current_user),
) -> list[str]:
    """
    Получает результат NER. На входе название номенклатуры, на выходе название компании производителя.
    """
    return brand_ner_model.get_all_ner_brands(text)