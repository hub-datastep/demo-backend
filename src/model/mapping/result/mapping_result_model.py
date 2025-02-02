from datetime import date
import re

from fastapi import HTTPException, status
from loguru import logger
from pandas import read_sql, DataFrame
from sqlalchemy import text
from sqlmodel import Session

from infra.env import UNISTROY_MAPPING_RESULTS_OUTPUT_TOPIC
from infra.kafka import send_message_to_kafka
from model.mapping.result import mapping_iteration_model
from model.tenant import tenant_model
from repository.mapping import mapping_iteration_repository, mapping_result_repository
from scheme.file.utd_card_message_scheme import (
    MappedMaterial,
    UTDCardMetadatas,
    UTDCardStatus,
    UTDCardOutputMessage,
)
from scheme.mapping.mapping_scheme import MappingOneNomenclatureRead
from scheme.mapping.result.mapping_iteration_scheme import MappingIteration
from scheme.mapping.result.mapping_result_scheme import (
    MappingResult,
    MappingResultUpdate,
    MappingResultsUpload,
)
from scheme.mapping.result.similar_nomenclature_search_scheme import (
    SimilarNomenclatureSearch,
    SimilarNomenclature,
)
from scheme.user.user_scheme import UserRead


SIMILAR_NOMS_COLUMNS = [
    "id",
    "name",
    "material_code",
]


def get_by_id(
    session: Session,
    result_id: int,
) -> MappingResult:
    mapping_result = mapping_result_repository.get_result_by_id(
        session=session,
        result_id=result_id,
    )

    if not mapping_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping Result with ID {result_id} not found",
        )

    return mapping_result


def _fetch_similar_noms(
    db_con_str: str,
    table_name: str,
    nomenclature_name: str,
    limit: int | None = 10,
    offset: int | None = 0,
) -> DataFrame:
    nomenclature_name = re.sub(r"\s+", "%", nomenclature_name)
    columns_str = ", ".join(f'"{col}"' for col in SIMILAR_NOMS_COLUMNS)

    st = text(
        f"""
        SELECT {columns_str}
        FROM {table_name}
        WHERE "name" ILIKE :nomenclature_name
        AND "is_group" = FALSE
        LIMIT {limit}
        OFFSET {offset}
        """
    ).bindparams(
        nomenclature_name=f"%{nomenclature_name}%",
    )

    return read_sql(st, db_con_str)


def get_similar_nomenclatures(
    session: Session,
    body: SimilarNomenclatureSearch,
    user: UserRead,
) -> list[SimilarNomenclature]:
    tenant = tenant_model.get_tenant_by_id(
        session=session,
        tenant_id=user.tenant_id,
    )
    tenant_db_uri = tenant.db_uri

    nomenclatures_table_name = user.classifier_config.nomenclatures_table_name

    nomenclature_name = body.name
    similar_noms_df = _fetch_similar_noms(
        db_con_str=tenant_db_uri,
        table_name=nomenclatures_table_name,
        nomenclature_name=nomenclature_name,
    )
    similar_noms_list = [
        SimilarNomenclature(**nom) for nom in similar_noms_df.to_dict(orient="records")
    ]

    return similar_noms_list


def save_mapping_results(
    mappings_list: list[MappingOneNomenclatureRead],
    user_id: int,
    iteration_id: str,
) -> list[MappingResult]:
    # Check if iteration with this ID exists
    try:
        mapping_iteration_model.get_iteration_by_id(iteration_id=iteration_id)
    except HTTPException:
        # Create iteration if not exists to not lose results
        iteration = MappingIteration(id=iteration_id)
        mapping_iteration_repository.create_iteration(iteration=iteration)

    results_list = []
    for mapping in mappings_list:
        mapping_dict = mapping.dict()
        mapping_result = MappingResult(
            iteration_id=iteration_id,
            user_id=user_id,
            result=mapping_dict,
        )
        results_list.append(mapping_result)

    return mapping_result_repository.create_mapping_results_list(
        mapping_results=results_list,
    )


def update_mapping_results_list(
    session: Session,
    body: MappingResultUpdate,
) -> list[MappingResult]:
    # Check if Mapping Iteration exists
    iteration_id = body.iteration_id
    mapping_iteration_model.get_iteration_by_id(
        iteration_id=iteration_id,
    )

    corrected_results_list: list[MappingResult] = []
    for corrected_result in body.corrected_results_list:
        result_id = corrected_result.result_id
        mapping_result = get_by_id(
            session=session,
            result_id=result_id,
        )
        mapping_result.corrected_nomenclature = corrected_result.nomenclature.dict()
        update_result = mapping_result_repository.update_result(
            session=session,
            mapping_result=mapping_result,
        )
        corrected_results_list.append(update_result)

    return corrected_results_list


def get_corrected_material_from_results(
    mapping_results_list: list[MappingResult],
    material: MappedMaterial,
) -> MappedMaterial | None:
    for mapping_result in mapping_results_list:
        result = MappingOneNomenclatureRead(**mapping_result.result)

        if (
            material.material_guid == result.material_code
            or material.idn_material_name == result.nomenclature
            or material.number == result.row_number
        ):
            if mapping_result.corrected_nomenclature:
                corrected_nomenclature = SimilarNomenclature(
                    **mapping_result.corrected_nomenclature,
                )
                material.material_guid = corrected_nomenclature.material_code
                break

    return material


async def upload_results_to_kafka(
    body: MappingResultsUpload,
) -> UTDCardOutputMessage:
    iteration_id = body.iteration_id
    iteration = mapping_iteration_model.get_iteration_by_id(iteration_id=iteration_id)
    mapping_results_list = iteration.results

    metadatas = UTDCardMetadatas(**iteration.metadatas)

    input_message = metadatas.input_message
    utd_entity = metadatas.entity
    check_results_output_message = metadatas.check_results_output_message

    mapped_materials = metadatas.mapped_materials

    # Replace with corrected materials
    for i, material in enumerate(mapped_materials):
        corrected_material = get_corrected_material_from_results(
            mapping_results_list=mapping_results_list,
            material=material,
        )
        mapped_materials[i] = corrected_material

    output_message = UTDCardOutputMessage(
        **input_message.dict(exclude={"guid"}),
        idn_card_guid=input_message.guid,
        guid=iteration_id,
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
        results_url=check_results_output_message.check_results_url,
    )

    logger.debug(f"Unistroy Kafka Response (output message):\n{output_message}")

    # Send message to Unistroy Kafka link-topic with url to check results
    await send_message_to_kafka(
        message_body=output_message.dict(),
        topic=UNISTROY_MAPPING_RESULTS_OUTPUT_TOPIC,
    )

    return output_message
