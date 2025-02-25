import traceback
from typing import Any, AsyncGenerator

from fastapi import HTTPException
from loguru import logger

from exception.utd_card_processing_exception import raise_utd_card_processing_exception
from infra.env import env
from model.file.utd.download_pdf_model import download_file
from model.file.utd.mappings_with_parsed_data_model import (
    add_parsed_data_to_mappings,
)
from model.file.utd.multi_entities_pdf_parsing_model import (
    extract_entities_with_params_and_noms,
)
from model.mapping.llm_mapping_model import (
    map_materials_list_with_llm,
    prepare_noms_for_mapping,
)
from model.mapping.result import mapping_iteration_model
from model.user import user_model
from scheme.file.utd_card_message_scheme import (
    UTDCardInputMessage,
    UTDCardCheckResultsOutputMessage,
    UTDCardMetadatas,
)
from scheme.mapping.result.mapping_iteration_scheme import (
    IterationMetadatasType,
    MappingIteration,
)
from util.json_serializing import serialize_obj
from util.uuid import generate_uuid

UNISTROY_USER_ID = 56


def _get_results_url(iteration_id: str) -> str:
    url = f"{env.FRONTEND_URL}/mapping/result/iteration/{iteration_id}"
    return url


async def parse_and_map_utd_card(
    body: UTDCardInputMessage,
) -> AsyncGenerator[UTDCardCheckResultsOutputMessage, Any]:
    try:
        credit_slip_data = body.credit_slip_data
        # Input materials category (group) guid
        category_guid = credit_slip_data.material_category_guid

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
                f"UTD Entity '{utd_entity.idn_number}' "
                f"with params and noms:\n{utd_entity}"
            )

            # Generate mapping iteration key (UTD guid)
            iteration_id = generate_uuid()

            # Get materials names list
            materials_with_params = utd_entity.nomenclatures_list
            materials_names_list = [
                nom.idn_material_name for nom in materials_with_params
            ]

            # Set index for each nomenclature
            # nomenclatures_with_indexes_list = get_noms_with_indexes(
            #     nomenclatures_list=materials_names_list,
            # )

            # Start mapping and wait results
            # mapping_results_jobs = start_mapping_and_wait_results(
            #     nomenclatures_list=nomenclatures_with_indexes_list,
            #     classifier_config=classifier_config,
            #     tenant_id=tenant_id,
            #     iteration_id=iteration_id,
            # )
            # logger.debug(f"Mapping Jobs:\n{mapping_results_jobs}")

            # Combine group code with materials names and add indexes
            materials_list = prepare_noms_for_mapping(
                materials_names_list=materials_names_list,
                group_code=category_guid,
            )
            # Start mapping with LLM
            mapping_results = map_materials_list_with_llm(
                materials_list=materials_list,
                classifier_config=classifier_config,
                tenant_id=tenant_id,
                iteration_id=iteration_id,
            )
            logger.debug(f"Mapping Results:\n{mapping_results}")

            # Get all nomenclatures from mapping results
            # mapping_results = extract_results_from_mapping_jobs(
            #     mapping_jobs=mapping_results_jobs,
            # )
            # Combine parsed materials and mapping results
            mapped_materials = add_parsed_data_to_mappings(
                parsed_materials=materials_with_params,
                mapping_results=mapping_results,
            )

            # Init url to mapping results
            results_url = _get_results_url(iteration_id=iteration_id)

            output_message = UTDCardCheckResultsOutputMessage(
                guid=iteration_id,
                idn_file_guid=idn_file_guid,
                building_guid=credit_slip_data.building_guid,
                material_category_guid=credit_slip_data.material_category_guid,
                check_results_url=results_url,
                **utd_entity.dict(),
            )

            # ! Remove this
            # Save mapping results for feedback
            # mapping_result_model.save_mapping_results(
            #     mappings_list=[
            #         MappingOneNomenclatureRead(
            #             row_number=material.number,
            #             internal_group=material.idn_material_name,
            #             nomenclature=material.idn_material_name,
            #         )
            #         for material in mapped_materials
            #     ],
            #     user_id=user.id,
            #     iteration_id=iteration_id,
            # )
            # ! #############

            # Create mapping iteration
            metadatas = UTDCardMetadatas(
                input_message=body,
                entity=utd_entity,
                mapped_materials=mapped_materials,
                check_results_output_message=output_message,
            )
            iteration = MappingIteration(
                id=iteration_id,
                # Save all known UTD data
                metadatas=serialize_obj(metadatas),
                # type=IterationMetadatasType.UTD.value,
                type=IterationMetadatasType.UTD_LLM.value,
            )
            mapping_iteration_model.create_or_update_iteration(
                iteration=iteration,
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
