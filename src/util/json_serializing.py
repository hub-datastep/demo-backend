import json
from datetime import date, datetime
from typing import Any

from pandas import Timestamp
from pydantic import BaseModel
from sqlmodel import SQLModel


def dataframe_serialer(obj: Any) -> str | None:
    if isinstance(obj, (Timestamp, datetime, date)):
        return obj.isoformat()
    return obj


def serialize_obj(obj: SQLModel | BaseModel | dict | None = None) -> dict | None:
    """
    Сериализует объект, делая их пригодными для сохранения в БД.
    """

    if not obj:
        return None

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


def serialize_objs_list(
    objs_list: list[SQLModel | dict] | None = None,
) -> list[dict | None] | None:
    """
    Сериализует список объектов, делая их пригодными для сохранения в БД.
    """

    if not objs_list:
        return None

    return [serialize_obj(obj) for obj in objs_list]
