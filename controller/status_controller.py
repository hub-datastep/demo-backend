from fastapi import APIRouter
from model.status_model import get_status

router = APIRouter(
    prefix="/status",
    tags=["status"],
)


@router.get("/")
def get_status_controller():
    return get_status()
