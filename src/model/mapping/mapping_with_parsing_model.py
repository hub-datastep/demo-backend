from fastapi import HTTPException
from loguru import logger
from rq.job import JobStatus

from exception.utd_card_processing_exception import raise_utd_card_processing_exception
from model.file.utd.download_pdf_model import download_file
from model.file.utd.mappings_with_parsed_data_model import add_parsed_data_to_mappings
from model.file.utd.pdf_parsing_model import extract_noms
from model.mapping.mapping_execute_model import get_noms_with_indexes, start_mapping_and_wait_results
from model.user import user_model
from scheme.file.utd_card_message_scheme import UTDCardInputMessage, UTDCardOutputMessage
from util.uuid import generate_uuid

UNISTROY_USER_ID = 56


def parse_and_map_utd_card(body: UTDCardInputMessage) -> UTDCardOutputMessage:
    try:
        first_utd_doc = body.documents[0]
        pdf_file_url = first_utd_doc.idn_link
        idn_file_guid = first_utd_doc.idn_file_guid

        # Download UTD pdf file
        file_bytes = download_file(file_url=pdf_file_url)

        # Parse nomenclatures from UTD pdf file
        nomenclatures_list = extract_noms(
            pdf_file_content=file_bytes,
            idn_file_guid=idn_file_guid,
        )
        logger.debug(f"Extracted noms:\n{nomenclatures_list}")
        nomenclatures_with_indexes_list = get_noms_with_indexes(nomenclatures_list)

        # Get Unistroy user and its params
        user = user_model.get_full_user_by_id(user_id=UNISTROY_USER_ID)
        classifier_config = user.classifier_config
        tenant_id = user.tenant_id

        # Start mapping and wait results
        mapping_results = start_mapping_and_wait_results(
            nomenclatures_list=nomenclatures_with_indexes_list,
            classifier_config=classifier_config,
            tenant_id=tenant_id,
        )
        logger.debug(f"Mapping Results:\n{mapping_results}")

        mapped_materials = add_parsed_data_to_mappings(
            mapping_results=mapping_results,
            # TODO: pass materials data from UTD
            # parsed_materials_data=parsed_materials_data,
        )

        output_message = UTDCardOutputMessage(
            **body.dict(),
            idn_guid=body.guid,
            guid=generate_uuid(),
            status=JobStatus.FINISHED,
            # Parsed Data
            # TODO: set parsed params from UTD pdf file
            # organization_inn=,
            # supplier_inn=,
            # idn_number=,
            # idn_date=,
            # correction_idn_number=,
            # correction_idn_date=,
            # contract_name=,
            # contract_number=,
            # contract_date=,
            # Mapping Data
            materials=mapped_materials,
        )

        return output_message

    # Handle our errors
    except HTTPException as e:
        error_str = e.detail
        return raise_utd_card_processing_exception(
            body=body,
            text=error_str,
        )

    # Handle unknown errors
    except Exception as e:
        error_str = str(e)
        return raise_utd_card_processing_exception(
            body=body,
            text=error_str,
        )
