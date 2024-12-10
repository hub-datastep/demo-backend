from fastapi import HTTPException
from scheme.parsing.parsing_scheme import UploadCardRequest, UploadCardResponse, Material
from model.parsing.parsing_utd import parsing_utd_file
from model.parsing.download_pdf import download_pdf
from model.parsing.webhook import kafka_request


def ParsingException(request:UploadCardRequest, text:str):
    return  UploadCardResponse(
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
        error_message= text
    )

def parsing_job(request: UploadCardRequest) -> bool:
    try:
        # Извлекаю номенклатуры из pdf файла по ссылке
        link_pdf_file = request.documents[0].idn_link
        uuid = request.documents[0].idn_file_guid.__str__()

        file = download_pdf(link_pdf_file)
        if type(file)==str:
            return ParsingException(request, file)
        
        nomenclatures = parsing_utd_file(file=file, uuid=uuid)
        if type(nomenclatures)==str:
            return ParsingException(request, nomenclatures)
        
        print(nomenclatures)
        # Тут должна быть логика маппинга


        # Допустим, распознано всё, кроме некоторых данных
        response = UploadCardResponse(
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
        # Возвращаем только тип ошибки и код из ошибки
        error_type = type(e).__name__
        error_code = str(e)
        return ParsingException(request, f"{error_type}: {error_code}")
