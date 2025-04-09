from typing import TypeAlias

MessageOrderParams: TypeAlias = tuple[
    # Order Id
    int,
    # CRM url
    str,
    # Address
    str,
    # Address with Apartment
    str,
    # Service Title (Name)
    str,
    # Resident Query
    str,
    # Created At str
    str,
    # Responsible Users Full Names
    list[str],
    # SLA timestamp
    int | None,
    # SLA left time in sec
    int | None,
    # SLA time text, e.g. "4 часа", "просрочен на 4 часа"
    str,
]
