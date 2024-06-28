from fastapi import APIRouter
from fastapi import Depends
from fastapi_versioning import version
from pydantic import BaseModel

from model.auth_model import get_current_user
from model.ner_brand_model import ner_model_instance
from scheme.user_scheme import UserRead

router = APIRouter()


@router.get("")
@version(1)
def get_ner_brand_results(
    *,
    text: str,
    current_user: UserRead = Depends(get_current_user),
) -> list[str]:
    """
    Получает результат ner. На входе название номенклатуры, на выходе название компании производителя
    """
    result = ner_model_instance.get_ner_brand(text)
    return result
