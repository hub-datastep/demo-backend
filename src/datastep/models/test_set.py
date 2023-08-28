from dataclasses import dataclass
from datetime import datetime

from datastep.utils.exclude_keys import exclude_keys


@dataclass
class TestSet:
    name: str
    description: str | None
    created_by: str | None
    created_at: datetime | None = None
    id: int = None

    def get_obj(self):
        return exclude_keys(self.__dict__, {"id", "created_at"})
