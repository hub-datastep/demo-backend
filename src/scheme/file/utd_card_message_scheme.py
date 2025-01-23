from datetime import date, datetime

from sqlmodel import SQLModel

"""
Все параметры, которые могут быть 'None' - парсятся из УПД PDF файла
"""


class UTDCardStatus:
    DONE = "DONE"
    ERROR = "ERROR"


class CreditSlipData(SQLModel):
    # Дата и время создания карточки УПД в тг боте
    idn_datetime: datetime
    # Email ответственного пользователя(тот кто нажал кнопку "отправить"),
    responsible_user_email: str
    # Вид операции(константа)
    operation_kind: str
    # guid объекта строительства
    building_guid: str
    # guid Генерального Подрядчика(сейчас это константа)
    gen_contractor_guid: str
    # guid категории материалов
    material_category_guid: str


class UTDDocument(SQLModel):
    # guid файла УПД
    idn_file_guid: str
    # Ссылка на скачивание файла УПД
    idn_link: str
    # Наименование файла
    idn_file_name: str


# * Схема входного сообщения из Кафки
class UTDCardInputMessage(SQLModel):
    # guid карточки подгрузки УПД (guid запроса)
    guid: str
    credit_slip_data: CreditSlipData
    documents: list[UTDDocument]


class SimilarMapping(SQLModel):
    # guid материала НСИ
    nomenclature_guid: str
    # Наименование материала НСИ
    nomenclature: str
    # Степень семантической схожести названия материала УПД с материалов НСИ
    # От 0 до 1
    similarity_score: float


class MappedMaterial(SQLModel):
    # Номер по списку
    number: int
    # Наименование материала как в УПД
    idn_material_name: str
    # guid материала (из справочника НСИ)
    material_guid: str | None = None
    # Материалы НСИ, похожие на материал УПД
    # Если material_guid=null, тогда не передается
    # Если material_guid is not null, тогда передаем
    similar_mappings: list[SimilarMapping] | None = None
    # Количество полученного материала
    quantity: float | None = None
    # Цена материала за единицу
    price: float | None = None
    # Сумма материала за весь объем
    cost: float | None = None
    # Ставка НДС (0.00 - если без НДС)
    vat_rate: float | None = None
    # Сумма НДС
    vat_amount: float | None = None


# * Схема выходного сообщения из Кафки
class UTDCardOutputMessage(SQLModel):
    # Data from Input Message
    credit_slip_data: CreditSlipData
    documents: list[UTDDocument]

    # Mapped data
    materials: list[MappedMaterial] | None = None

    # guid карточки подгрузки УПД (guid запроса)
    idn_card_guid: str
    # guid сущности УПД (создается и присваивается в нейросети)
    guid: str | None = None
    # Статус распознавания
    status: str
    # ИНН организации (покупатель со стороны Унистрой)
    organization_inn: str | None = None
    # ИНН поставщика
    supplier_inn: str | None = None
    # Номер УПД
    idn_number: str | None = None
    # Дата УПД
    idn_date: date | None = None
    # Номер исправления УПД (Integrated Delivery Note)
    correction_idn_number: str | None = None
    # Дата исправления УПД
    correction_idn_date: date | None = None
    # Наименование договора поставки
    contract_name: str | None = None
    # Номер договора поставки
    contract_number: str | None = None
    # Дата договора поставки
    contract_date: date | None = None
    # Сообщение об ошибке
    error_message: str | None = None

    # URL to web interface with results
    results_url: str


class UTDEntityWithParamsAndNoms(SQLModel):
    idn_number: str | None = None
    idn_date: date | None = None
    supplier_inn: str | None = None
    pages_numbers_list: list[int] = []
    nomenclatures_list: list[str] | None = None


# * Схема выходного сообщения из Кафки со ссылкой на результаты для проверки
class UTDCardCheckResultsOutputMessage(SQLModel):
    # guid карточки подгрузки УПД (guid запроса)
    guid: str
    # guid файла УПД
    idn_file_guid: str
    # guid объекта строительства
    building_guid: str
    # guid категории материалов
    material_category_guid: str
    # Ссылка на проверку результата
    check_results_url: str
    # ИНН поставщика
    supplier_inn: str | None = None
    # Наименование договора поставки
    contract_name: str | None = None


class UTDCardMetadatas(SQLModel):
    input_message: UTDCardInputMessage
    entity: UTDEntityWithParamsAndNoms
    mapped_materials: list[MappedMaterial] | None
    check_results_output_message: UTDCardCheckResultsOutputMessage
