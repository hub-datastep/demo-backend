from pydantic import BaseModel, EmailStr, UUID4
from typing import List, Optional
from datetime import datetime

# Модели данных для валидации входящих данных
class Document(BaseModel):
    idn_file_guid: UUID4
    idn_link: str
    idn_file_name: str

class UploadCardRequest(BaseModel):
    guid: UUID4
    idn_datetime: datetime
    responsible_user_email: EmailStr
    operation_kind: str
    building_guid: UUID4
    contractor_guid: UUID4
    documents: List[Document]

class Material(BaseModel):
    number: int
    material_guid: UUID4
    quantity: float
    price: float
    cost: float
    vat_rate: float
    vat_amount: float

# Модели для выходных данных
class UploadCardResponse(BaseModel):
    guid: UUID4
    contractor_guid: UUID4
    responsible_user_email: EmailStr
    operation_kind: str
    building_guid: UUID4
    documents: List[Document]
    materials: Optional[List] = None
    idn_guid: UUID4
    organization_inn: Optional[str] = None
    supplier_inn: Optional[str] = None
    idn_number: Optional[str] = None
    idn_date: Optional[str] = None
    correction_idn_number: Optional[str] = None
    correction_idn_date: Optional[str] = None
    contract_name: Optional[str] = None
    contract_number: Optional[str] = None
    contract_date: Optional[str] = None
    status: str
    error_message: Optional[str] = None
