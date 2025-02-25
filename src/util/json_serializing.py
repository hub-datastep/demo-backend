from datetime import datetime
import json
from typing import Any

from pandas import Timestamp
from pydantic import BaseModel
from sqlmodel import SQLModel


def dataframe_serialer(obj: Any) -> str | None:
    if isinstance(obj, Timestamp) or isinstance(obj, datetime):
        return obj.isoformat()


def serialize_obj(obj: SQLModel | BaseModel | dict) -> dict:
    """
    Сериализует объект, делая их пригодными для сохранения в БД.
    """

    # Convert custom schemas to dict
    obj_dict: dict
    if isinstance(obj, SQLModel) or isinstance(obj, BaseModel):
        obj_dict = obj.dict()
    else:
        obj_dict = obj

    # Serialize object
    serialized_obj: dict = json.loads(
        json.dumps(
            obj_dict,
            ensure_ascii=False,
            default=dataframe_serialer,
        )
    )

    return serialized_obj


def serialize_objs_list(objs_list: list[SQLModel | dict]) -> list[dict]:
    """
    Сериализует список объектов, делая их пригодными для сохранения в БД.
    """

    return [serialize_obj(obj) for obj in objs_list]
