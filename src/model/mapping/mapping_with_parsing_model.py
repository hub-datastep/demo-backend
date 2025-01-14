import traceback
from datetime import date
from typing import Any, AsyncGenerator

from fastapi import HTTPException
from loguru import logger

from exception.utd_card_processing_exception import raise_utd_card_processing_exception
from infra.env import FRONTEND_URL
from model.file.utd.download_pdf_model import download_file
from model.file.utd.mappings_with_parsed_data_model import add_parsed_data_to_mappings
from model.file.utd.multi_entities_pdf_parsing_model import (
    extract_entities_with_params_and_noms,
)
from model.mapping.mapping_execute_model import (
    get_noms_with_indexes,
    start_mapping_and_wait_results,
)
from model.user import user_model
from scheme.file.utd_card_message_scheme import (
    UTDCardInputMessage,
    UTDCardOutputMessage,
    UTDCardStatus,
)
from util.uuid import generate_uuid

UNISTROY_USER_ID = 56

RESULTS_URL_BASE = f"{FRONTEND_URL}/classifier/history?iteration_key="


async def parse_and_map_utd_card(
    body: UTDCardInputMessage,
) -> AsyncGenerator[UTDCardOutputMessage, Any]:
    try:
        first_utd_doc = body.documents[0]
        pdf_file_url = first_utd_doc.idn_link
        idn_file_guid = first_utd_doc.idn_file_guid

        # Download UTD pdf file
        file_bytes = download_file(file_url=pdf_file_url)

        # Parse params and nomenclatures from UTD pdf file
        utd_entities_with_params_and_noms = extract_entities_with_params_and_noms(
            pdf_file=file_bytes,
            idn_file_guid=idn_file_guid,
        )

        # Get Unistroy user and its params
        user = user_model.get_full_user_by_id(user_id=UNISTROY_USER_ID)
        classifier_config = user.classifier_config
        tenant_id = user.tenant_id

        for utd_entity in utd_entities_with_params_and_noms:
            logger.debug(
                f"UTD Entity '{utd_entity.idn_number}' with params and noms:\n{utd_entity}"
            )

            # Generate mapping iteration key (UTD guid)
            iteration_key = generate_uuid()

            # Set index for each nomenclature
            nomenclatures_list = utd_entity.nomenclatures_list
            nomenclatures_with_indexes_list = get_noms_with_indexes(nomenclatures_list)

            # Start mapping and wait results
            mapping_results = start_mapping_and_wait_results(
                nomenclatures_list=nomenclatures_with_indexes_list,
                classifier_config=classifier_config,
                tenant_id=tenant_id,
                iteration_key=iteration_key,
            )
            logger.debug(f"Mapping Results:\n{mapping_results}")

            mapped_materials = add_parsed_data_to_mappings(
                mapping_results=mapping_results,
                # TODO: pass materials data from UTD
                parsed_materials_data=[],
            )

            output_message = UTDCardOutputMessage(
                **body.dict(exclude={"guid"}),
                idn_card_guid=body.guid,
                guid=iteration_key,
                status=UTDCardStatus.DONE,
                # Mapping Data
                materials=mapped_materials,
                # Parsed Data
                supplier_inn=utd_entity.supplier_inn,
                idn_number=utd_entity.idn_number,
                idn_date=utd_entity.idn_date,
                # TODO: set parsed params from UTD pdf file
                # ! Now it's mocked data
                organization_inn="3305061878",
                correction_idn_number="НО-12865РД/2",
                correction_idn_date=date(2024, 8, 27),
                contract_name="ДОГОВОР ПОСТАВКИ № 003/06-Лето от 13.09.2023",
                contract_number="003/06-Лето",
                contract_date=date(2024, 8, 27),
                # URL to web interface with results
                results_url=f"{RESULTS_URL_BASE}{iteration_key}",
            )

            yield output_message

    # Handle our errors
    except HTTPException as e:
        error_traceback = traceback.format_exc()
        logger.error(error_traceback)
        error_str = e.detail
        yield raise_utd_card_processing_exception(
            body=body,
            error_message=error_str,
        )

    # Handle unknown errors
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(error_traceback)
        error_str = str(e)
        yield raise_utd_card_processing_exception(
            body=body,
            error_message=error_str,
        )
