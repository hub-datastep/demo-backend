from dataclasses import dataclass

from datastep.utils.exclude_keys import exclude_keys


@dataclass
class Test:
    question: str
    answer: str
    sql: str
    table: str
    is_exception: bool
    exception: str | None
    test_id: int
    id: int = None

    def get_obj(self):
        return exclude_keys(self.__dict__, {"id"})
