from fastapi import APIRouter
from fastapi import Depends
from fastapi_versioning import version

from model.auth.auth_model import get_current_user
from model.ner.ner import ner_model
from scheme.user.user_scheme import UserRead

router = APIRouter()


@router.get("", response_model=str)
@version(1)
def get_ner_brand_results(
    text: str,
    current_user: UserRead = Depends(get_current_user),
) -> str:
    response = ner_model.predict([text])
    if response:
        return response[0]
    return ""

@router.get("/all", response_model=list[str])
@version(1)
def get_all_ner_brand_results(
    text: list[str],
    current_user: UserRead = Depends(get_current_user),
) -> list[str]:
    response = ner_model.predict(text)
    return response