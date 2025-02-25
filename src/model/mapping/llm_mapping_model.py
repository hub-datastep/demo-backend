from chromadb import Collection, Documents, IDs, Metadata, QueryResult, Where
from fastapi import HTTPException, status
from langchain.chains.llm import LLMChain
from loguru import logger
from numpy import ndarray
from pandas import read_sql
from sqlmodel import Session

from infra.chroma_store import connect_to_chroma_collection, get_embeddings
from infra.database import engine
from infra.llm_clients_credentials import Client
from llm.chain.mapping.mapping_chain import get_llm_mapping_chain, run_llm_mapping
from model.classifier import classifier_config_model
from model.mapping.result import mapping_result_model
from model.used_token import used_token_model
from scheme.classifier.classifier_config_scheme import ClassifierConfig
from scheme.mapping.llm_mapping_scheme import (
    LLMMappingKnowledgeBaseCase,
    LLMMappingResult,
)
from scheme.mapping.mapping_scheme import (
    MappingOneNomenclatureUpload,
    MappingOneTargetRead,
)
from util.json_serializing import serialize_obj, serialize_objs_list
from util.uuid import generate_uuid

# Count of item in response from vectorstore
NSI_MOST_SIMILAR_COUNT = 30
KB_MOST_SIMILAR_COUNT = 30

# Knowledge Base vectorstore collection name
KB_COLLECTION_NAME = "unistroy_knowledge_base"


def get_noms_filters(group: str) -> Where:
    """
    Собирает фильтры для поиска в НСИ (коллекции векторстора).
    """

    filters = {"group": f"{group}"}
    return filters


def get_kb_filters(group: str) -> Where:
    """
    Собирает фильтры для поиска в Базе Знаний (коллекции векторстора).
    """

    filters = {"Класс УПД материала": f"{group}"}
    return filters


def get_collection_items(
    collection: Collection,
    embeddings: ndarray,
    filters: Where,
    most_similar_count: int | None = 3,
) -> tuple[IDs, Documents, list[Metadata | dict], list[float]]:
    """
    Выбирает ближайшие `<most_similar_count>` векторов из переданной коллекции
    векторстора по переданным фильтрам.

    И возвращает
    - ID векторов
    - Наименования (текстовое представление векторов)
    - Метадату
    - Расстояние от переданного вектора
    """

    response: QueryResult = collection.query(
        query_embeddings=embeddings.tolist(),
        where=filters,
        n_results=most_similar_count,
        include=[
            "documents",
            "distances",
            "metadatas",
        ],
    )
    # logger.debug(f"Collection '{collection.name}' response: {response}")

    ids = response["ids"][0]
    names = response["documents"][0]
    metadatas = response["metadatas"][0]
    distances = response["distances"][0]

    return ids, names, metadatas, distances


def get_data_from_nsi(
    collection: Collection,
    material_embeddings: ndarray,
    material_group: str,
    most_similar_count: int = 3,
) -> tuple[IDs, Documents, list[Metadata | dict], list[float]]:
    """
    Получает ближайшие `<most_similar_count>` номенклатур из НСИ.
    """

    filters = get_noms_filters(group=material_group)

    response = get_collection_items(
        collection=collection,
        embeddings=material_embeddings,
        filters=filters,
        most_similar_count=most_similar_count,
    )

    return response


def get_noms_to_str(noms_names: list[str]) -> str:
    """
    Собирает список наименований номенклатур в ненумерованный список.
    """

    return "".join([f"\n- '{name}'" for name in noms_names])


def get_data_from_kb(
    collection: Collection,
    material_embeddings: ndarray,
    material_group: str,
    most_similar_count: int = 3,
) -> tuple[IDs, Documents, list[dict], list[float]]:
    """
    Получает ближайшие `<most_similar_count>` кейсов
    из Базы Знаний (истории сопоставлений).
    """

    filters = get_kb_filters(group=material_group)

    response = get_collection_items(
        collection=collection,
        embeddings=material_embeddings,
        filters=filters,
        most_similar_count=most_similar_count,
    )

    return response


def combine_mapping_history(
    materials_names_list: list[str],
    metadatas_list: list[dict],
) -> list[LLMMappingKnowledgeBaseCase]:
    """
    Преобразует материалы и их метадату (данные из векторстора) в объекты по схеме.
    """

    mapping_history: list[LLMMappingKnowledgeBaseCase] = []

    for name, metadata in zip(materials_names_list, metadatas_list):
        # Входной материал
        input_material = name
        # Предсказанный НСИ материал
        predicted_material = metadata.get("Предсказанный НСИ материал")
        # Правильное или Неправильное сопоставление
        is_correct = metadata.get("Правильное предсказание?")
        # Фидбек на сопоставление
        feedback = metadata.get("Фидбек Оператора")
        # Правильный НСИ материал
        correct_material = metadata.get("Правильный материал НСИ")

        mapping_history.append(
            LLMMappingKnowledgeBaseCase(
                input_material=input_material,
                predicted_nomenclature=predicted_material,
                is_correct=is_correct,
                feedback=feedback,
                correct_nomenclature=correct_material,
            )
        )

    return mapping_history


def get_mapping_history_to_str(
    kb_cases_list: list[LLMMappingKnowledgeBaseCase],
) -> str:
    """
    Собирает из списка кейсов из Базы Знаний (истории сопоставлений) ненумерованный
    список по схеме.
    """

    mapping_history_str: str = ""
    for i, case in enumerate(kb_cases_list):
        # Replace bool param 'is_correct' with text
        is_correct_str = None
        # Check if 'is_correct' is set
        is_correct = case.is_correct
        if isinstance(is_correct, bool):
            if is_correct:
                is_correct_str = "правильное сопоставление"
            else:
                is_correct_str = "неправильное сопоставление"

        # Combine case to str
        mapping_history_str += f"""
- Кейс {i}
    - Входной УПД материал: '{case.input_material}'
    - Предсказанный НСИ материал: '{case.predicted_nomenclature}'
    - Правильно/Неправильно: '{is_correct_str}'
    - Объяснение: '{case.feedback}'
    - Правильный НСИ материал: '{case.correct_nomenclature}'
"""
    return mapping_history_str


def _get_group_by_code(
    classifier_config: ClassifierConfig,
    group_code: str,
) -> dict:
    """
    Получает все данные о группе в НСИ по её коду.
    """

    # Get NSI table name
    table_name = classifier_config.nomenclatures_table_name

    # Get group from NSI table
    with Session(engine) as session:
        query = f"""
            SELECT *
            FROM {table_name}
            WHERE "material_code" = %(group_code)s
            AND "is_group" = TRUE
            LIMIT 1
            OFFSET 0
        """
        group_df = read_sql(
            query,
            session.bind,
            params={"group_code": group_code},
        )

        # Check if group found
        if group_df.empty:
            raise HTTPException(
                status_code=status,
                detail=f"Category with guid '{group_code}' not found",
            )

        # Get first response item
        group = group_df.iloc[0].to_dict()
        return group


def _get_nomenclature_by_name(
    classifier_config: ClassifierConfig,
    nomenclature_name: str,
) -> dict:
    """
    Получает все данные о номенклатуре в НСИ по её наименованию.
    """

    # Get NSI table name
    table_name = classifier_config.nomenclatures_table_name

    # Get nomenclature from NSI table
    with Session(engine) as session:
        query = f"""
            SELECT *
            FROM {table_name}
            WHERE "name" ILIKE %(nomenclature_name)s
            AND "is_group" = FALSE
            LIMIT 1
            OFFSET 0
        """
        nomenclature_df = read_sql(
            query,
            session.bind,
            params={"nomenclature_name": nomenclature_name},
        )

        # Check if nomenclature found
        if nomenclature_df.empty:
            return None

        # Get first response item
        nomenclature = nomenclature_df.iloc[0].to_dict()
        return nomenclature


def _get_similar_nomenclature(
    chain: LLMChain,
    classifier_config: ClassifierConfig,
    material: MappingOneNomenclatureUpload,
    noms_collection: Collection,
    kb_collection: Collection,
) -> LLMMappingResult:
    """
    Сопоставляет входной материал с номенклатурой из НСИ с помощью LLM.
    """

    # Extract material params
    row_number = material.row_number
    material_name = material.nomenclature
    group_code = material.group_code

    # Get embeddings from material name
    embeddings = get_embeddings(texts_list=[material_name])[0]

    # Get material group by code (category guid in Kafka input message)
    group = _get_group_by_code(
        classifier_config=classifier_config,
        group_code=group_code,
    )
    material_group = group.get("name")

    # Get Data from Knowledge Base
    _, kb_response_names, kb_response_metadatas, _ = get_data_from_kb(
        collection=kb_collection,
        material_embeddings=embeddings,
        material_group=material_group,
        most_similar_count=KB_MOST_SIMILAR_COUNT,
    )
    kb_cases_list = combine_mapping_history(
        materials_names_list=kb_response_names,
        metadatas_list=kb_response_metadatas,
    )
    kb_cases_list_str = get_mapping_history_to_str(kb_cases_list=kb_cases_list).strip()

    # Get Data from NSI
    _, nom_response_names, _, _ = get_data_from_nsi(
        collection=noms_collection,
        material_embeddings=embeddings,
        material_group=material_group,
        most_similar_count=NSI_MOST_SIMILAR_COUNT,
    )
    nsi_materials_names_str = get_noms_to_str(nom_response_names).strip()

    # Run LLM Chain
    chain_response = run_llm_mapping(
        chain=chain,
        material_name=material_name,
        kb_cases_list_str=kb_cases_list_str,
        nsi_materials_names_str=nsi_materials_names_str,
    )
    result_nomenclature_name = chain_response.nomenclature

    # Get all nomenclature data from NSI table
    nsi_nomenclature = _get_nomenclature_by_name(
        classifier_config=classifier_config,
        nomenclature_name=result_nomenclature_name,
    )
    # Extract material code from NSI nomenclature
    material_code: str | None = None
    material_code: str | None = None
    if nsi_nomenclature:
        material_id = str(nsi_nomenclature.get("id"))
        material_code = nsi_nomenclature.get("material_code")

    # Combine chain response to result schema
    result = LLMMappingResult(
        # * Mapped Nomenclature data
        row_number=row_number,
        nomenclature=material_name,
        group=material_group,
        group_code=group_code,
        mappings=[
            MappingOneTargetRead(
                nomenclature_guid=material_id,
                group=material_group,
                group_code=group_code,
                material_code=material_code,
                nomenclature=result_nomenclature_name,
            ),
        ],
        # * LLM response & additional data
        full_response=serialize_obj(chain_response),
        llm_comment=chain_response.comment,
        nomenclature_data=serialize_obj(nsi_nomenclature),
        nsi_nomenclatures_list=nom_response_names,
        knowledge_base_cases_list=serialize_objs_list(kb_cases_list),
    )

    return result


def map_materials_list_with_llm(
    materials_list: list[MappingOneNomenclatureUpload],
    classifier_config: ClassifierConfig,
    tenant_id: int,
    iteration_id: str,
) -> list[LLMMappingResult]:
    """
    Запускает маппинг (с помощью LLM) переданного списка материалов
    с номенклатурами из НСИ.
    По завершении маппинга сохраняет результаты и кол-во потраченных токенов в БД.
    """

    user_id = classifier_config.user_id

    logger.debug(
        f"Classifier config for user with ID '{user_id}':\n{classifier_config}"
    )

    # Connect to NSI vectorstore collection
    noms_collection_name = classifier_config.chroma_collection_name
    noms_collection = connect_to_chroma_collection(
        collection_name=noms_collection_name,
    )

    # Connect to Knowledge Base vectorstore collection
    kb_collection = connect_to_chroma_collection(
        collection_name=KB_COLLECTION_NAME,
    )

    # Init Mapping Chain
    chain = get_llm_mapping_chain(client=Client.UNISTROY)

    # Run mapping of passed materials
    mapping_results: list[LLMMappingResult] = []
    for material in materials_list:
        # Map material to NSI nomenclature
        result = _get_similar_nomenclature(
            chain=chain,
            classifier_config=classifier_config,
            material=material,
            noms_collection=noms_collection,
            kb_collection=kb_collection,
        )
        mapping_results.append(result)

    # Save mapping results for feedback
    mapping_result_model.save_mapping_results(
        mappings_list=mapping_results,
        user_id=user_id,
        iteration_id=iteration_id,
    )

    # Charge tenant used tokens for nomenclatures mapping
    tokens_count = used_token_model.count_used_tokens(mapping_results)
    used_token_model.charge_used_tokens(
        tokens_count=tokens_count,
        tenant_id=tenant_id,
        user_id=user_id,
    )

    return mapping_results


if __name__ == "__main__":
    with Session(engine) as session:
        config = classifier_config_model.get_classifier_config_by_user_id(
            session=session,
            user_id=1,
        )
    materials_list = [
        MappingOneNomenclatureUpload(
            row_number=1,
            nomenclature="ВВГнг(А)-LS 5х2,5-0,66 кабель ВЭКЗ VEKZ00064",
            group_code="7d1e4f55-60ce-11ed-b567-b49691c49eb4",
        )
    ]
    tenant_id = 1
    iteration_id = generate_uuid()

    results = map_materials_list_with_llm(
        materials_list=materials_list,
        classifier_config=config,
        tenant_id=tenant_id,
        iteration_id=iteration_id,
    )
    logger.info(f"{results}")
