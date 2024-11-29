import pdfplumber
from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter()

from pydantic import BaseModel, EmailStr, UUID4
from typing import List, Optional
from datetime import datetime

# Модели данных для валидации входящих данных
class Document(BaseModel):
    idn_file_guid: UUID4
    idn_link: str
    idn_file_name: str

class Material(BaseModel):
    number: int
    material_guid: UUID4
    quantity: float
    price: float
    cost: float
    vat_rate: float
    vat_amount: float



@router.post("/parsing/")
async def create_upload_card(request: Document):
    try:
        # Здесь будет логика обработки данных (например, распознавание, извлечение информации из файла)

        # Допустим, распознано всё, кроме некоторых данных
        response = Material(
            guid=request.guid,
            contractor_guid=request.contractor_guid,
            responsible_user_email=request.responsible_user_email,
            operation_kind=request.operation_kind,
            building_guid=request.building_guid,
            documents=request.documents,
            materials=[  # Пример распознанных материалов
                Material(
                    number=1,
                    material_guid="d7a4b91d-a025-4e69-9872-06fc67f0c762",
                    quantity=16.25,
                    price=100.00,
                    cost=1625.00,
                    vat_rate=20.00,
                    vat_amount=1946.40,
                )
            ],
            idn_guid=request.guid,  # Используем тот же guid для сущности УПД
            organization_inn="3305061878",  # Пример распознанного ИНН организации
            supplier_inn="4629044850",  # Пример распознанного ИНН поставщика
            idn_number="НО-12865РД",  # Пример распознанного номера УПД
            idn_date="2024-10-16",  # Пример распознанной даты УПД
            correction_idn_number="НО-12865РД/2",  # Пример исправленного номера
            correction_idn_date="2024-10-18",  # Пример исправленной даты
            contract_name="ДОГОВОР ПОСТАВКИ № 003/06-Лето от 13.09.2023",  # Пример распознанного наименования договора
            contract_number="003/06-Лето",  # Пример распознанного номера договора
            contract_date="2023-09-13",  # Пример распознанной даты договора
            status="DONE",  # Статус успешного распознавания
            error_message=None  # Нет ошибки
        )

        return response

    except Exception as e:
        # В случае ошибки, возвращаем ошибку распознавания
        response = UploadCardResponse(
            guid=request.guid,
            contractor_guid=request.contractor_guid,
            responsible_user_email=request.responsible_user_email,
            operation_kind=request.operation_kind,
            building_guid=request.building_guid,
            documents=request.documents,
            materials=None,
            idn_guid=request.guid,
            organization_inn=None,
            supplier_inn=None,
            idn_number=None,
            idn_date=None,
            correction_idn_number=None,
            correction_idn_date=None,
            contract_name=None,
            contract_number=None,
            contract_date=None,
            status="ERROR",
            error_message=f"Ошибка распознавания: {str(e)}"
        )
        return response

