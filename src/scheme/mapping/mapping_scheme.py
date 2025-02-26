from sqlmodel import SQLModel


class MappingOneNomenclatureUpload(SQLModel):
    row_number: int
    nomenclature: str
    group_code: str | None = None


class MappingOneTargetRead(SQLModel):
    nomenclature_guid: str | None
    group: str | None
    group_code: str | None
    view: str | None
    view_code: str | None
    material_code: str | None
    nomenclature: str
    similarity_score: float | None


class MappingOneNomenclatureRead(SQLModel):
    # Номер материала посчёту
    row_number: int
    # Входной материал
    nomenclature: str
    # Внутренняя группа входного материала
    internal_group: str | None
    # Группа входного материала
    group: str | None
    # Код(guid) группы входного материала
    group_code: str | None
    # Вид/Тип входного материала
    view: str | None
    # Код(guid) Вида/Типа входного материала
    view_code: str | None
    # guid смапленной НСИ номенклатуры
    material_code: str | None
    # Список спаршенных параметров входного материала
    nomenclature_params: list[dict] | None
    # Смапленная НСИ номенклатура
    mappings: list[MappingOneTargetRead] | None
    # Варианты похожих НСИ номенклатур
    similar_mappings: list[MappingOneTargetRead] | None


class MappingNomenclaturesUpload(SQLModel):
    nomenclatures: list[MappingOneNomenclatureUpload]
    most_similar_count: int = 3
    chunk_size: int = 100


class MappingNomenclaturesResultRead(SQLModel):
    job_id: str
    ready_count: int | None
    total_count: int | None
    general_status: str
    nomenclatures: list[MappingOneNomenclatureRead] | None
