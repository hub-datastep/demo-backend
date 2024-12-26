from datetime import datetime

import joblib
import numpy as np
from chromadb import QueryResult, Where
from chromadb.api.models.Collection import Collection
from fastapi import HTTPException, status
from fastembed import TextEmbedding
from loguru import logger
from pandas import DataFrame
from rq import get_current_job
from rq.job import JobStatus
from tqdm import tqdm

from infra.chroma_store import connect_to_chroma_collection, get_all_collections
from infra.redis_queue import MAX_JOB_TIMEOUT, QueueName, get_job, get_redis_queue
from model.classifier.classifier_retrain_model import TRAINING_COLUMNS
from model.classifier.classifier_version_model import get_model_path
from model.mapping.group_views_model import get_nomenclatures_views
from model.mapping.mapping_result_model import save_mapping_result
from model.ner.ner import ner_service
from model.used_token.used_token_model import charge_used_tokens, count_used_tokens
from scheme.classifier.classifier_config_scheme import ClassifierConfig
from scheme.mapping.mapping_scheme import (MappingNomenclaturesResultRead, MappingOneNomenclatureRead,
                                           MappingOneNomenclatureUpload, MappingOneTargetRead)
from scheme.task.task_scheme import JobIdRead
from util.extract_keyword import extract_keyword
from util.features_extraction import extract_features, get_noms_metadatas_with_features
from util.normalize_name import normalize_name
from util.uuid import generate_uuid

tqdm.pandas()
# noinspection PyTypeChecker
np.set_printoptions(threshold=np.inf)


def _get_nomenclatures_groups_old(
    noms: DataFrame,
    model_id: str,
    is_use_params: bool,
) -> list[str]:
    model_path = get_model_path(model_id)
    model = joblib.load(model_path)

    # If without params -> use only "normalized" column
    if is_use_params:
        final_training_columns = TRAINING_COLUMNS
    else:
        final_training_columns = TRAINING_COLUMNS[0]

    prediction_df = noms[final_training_columns]
    predicted_groups = model.predict(prediction_df)

    return predicted_groups


def get_nomenclatures_groups(
    noms: DataFrame,
    model_id: str,
) -> list[str]:
    model_path = get_model_path(model_id)
    model_packages = joblib.load(model_path)
    logger.info(f"model packages: {model_packages}")

    model = model_packages['model']
    label_encoder = model_packages['label_encoder']

    prediction_df = noms['nomenclature']
    prediction_list = prediction_df.to_list()

    # Predict groups ids and encode them to groups names
    predicted_groups = label_encoder.inverse_transform(
        model.predict(prediction_list),
    )

    return predicted_groups


def _build_where_metadatas_old(
    group: str,
    brand: str | None,
    view: str | None,
    metadatas_list: list[dict] | None,
    is_hard_params: bool,
    is_params_needed: bool,
    is_brand_needed: bool,
    is_view_needed: bool,
):
    if len(metadatas_list) == 0 or not is_params_needed:
        # where_metadatas = {"$and": [
        #     {"group": group},
        #     {"brand": brand},
        # ]}
        where_metadatas = {"group": group}
    else:
        metadatas_list_with_group = [{"group": group}]
        for metadata in metadatas_list:
            metadatas_list_with_group.append(metadata)

        # Get metadatas for hard-search
        if is_hard_params:
            where_metadatas = {"$and": metadatas_list_with_group}
        # Get metadatas for soft-search
        else:
            where_metadatas = {"$or": metadatas_list_with_group}

    return where_metadatas


def build_where_metadatas(
    group: str,
    brand: str | None,
    view: str | None,
    metadatas_list: list[dict] | None,
    is_hard_params: bool,
    is_params_needed: bool,
    is_brand_needed: bool,
    is_view_needed: bool,
) -> Where:
    conditions = [{"internal_group": group}]

    additional_conditions = []

    if is_params_needed:
        additional_conditions.extend(metadatas_list)

    if is_brand_needed:
        additional_conditions.append({"brand": brand})

    if is_view_needed:
        additional_conditions.append({"view": view})

    if is_hard_params:
        if len(additional_conditions) > 0:
            conditions.extend(additional_conditions)
            return {"$and": conditions}
        else:
            return conditions[0]
    else:
        if len(additional_conditions) > 1:
            return {"$and": [conditions[0], {"$or": additional_conditions}]}
        elif len(additional_conditions) == 1:
            conditions.extend(additional_conditions)
            return {"$or": [conditions[0], {"$and": conditions}]}
        else:
            return conditions[0]


def map_on_nom(
    collection: Collection,
    nom_embeddings: np.ndarray,
    group: str,
    brand: str | None,
    view: str | None,
    metadatas_list: list[dict] | None,
    is_hard_params: bool,
    is_use_params: bool,
    is_use_brand_recognition: bool,
    is_use_view_classification: bool,
    most_similar_count: int = 1,
) -> list[MappingOneTargetRead] | None:
    is_params_exists = metadatas_list is not None and len(metadatas_list) > 0
    is_params_needed = is_params_exists and is_use_params

    is_brand_exists = brand is not None
    is_brand_needed = is_brand_exists and is_use_brand_recognition

    is_view_exists = view is not None
    is_view_needed = is_view_exists and is_use_view_classification

    # where_metadatas = _build_where_metadatas_old(
    where_metadatas = build_where_metadatas(
        group=group,
        brand=brand,
        view=view,
        metadatas_list=metadatas_list,
        is_hard_params=is_hard_params,
        is_params_needed=is_params_needed,
        is_brand_needed=is_brand_needed,
        is_view_needed=is_view_needed,
    )

    nom_embeddings = nom_embeddings.tolist()
    response: QueryResult = collection.query(
        query_embeddings=[nom_embeddings],
        where=where_metadatas,
        n_results=most_similar_count,
        include=["documents", "distances", "metadatas"],
    )

    response_ids = response['ids'][0]

    if len(response_ids) == 0:
        return None

    response_documents = response['documents'][0]
    response_metadatas = response['metadatas'][0]
    response_distances = response['distances'][0]

    mapped_noms = []
    for i in range(len(response_ids)):
        group = response_metadatas[i].get("group")
        group_code = response_metadatas[i].get("group_code")
        view_code = response_metadatas[i].get("view_code")
        material_code = response_metadatas[i].get("material_code")

        mapped_noms.append(
            MappingOneTargetRead(
                nomenclature_guid=response_ids[i],
                nomenclature=response_documents[i],
                group=group,
                group_code=group_code,
                view_code=view_code,
                material_code=material_code,
                similarity_score=response_distances[i],
            )
        )

    return mapped_noms


# param arg can be: group, group_code, view_code, material_code
def _get_mappings_param(param: str, mappings_list: list[MappingOneTargetRead]) -> str:
    param_values = []

    for mapping in mappings_list:
        if param == "group":
            param_values.append(mapping.group)
        if param == "group_code":
            param_values.append(mapping.group_code)
        if param == "view_code":
            param_values.append(mapping.view_code)
        if param == "material_code":
            param_values.append(mapping.material_code)

    param_values_as_str = "\n".join(param_values)
    return param_values_as_str


def convert_nomenclatures_to_df(nomenclatures: list[MappingOneNomenclatureUpload]) -> DataFrame:
    nomenclatures_as_json = [nom.dict().values() for nom in nomenclatures]
    return DataFrame(nomenclatures_as_json, columns=['row_number', 'nomenclature'])


def get_nomenclatures_embeddings(strings: list[str]) -> list[np.ndarray]:
    embedding_model = TextEmbedding(
        model_name="intfloat/multilingual-e5-large"
    )
    strings = [f"query: {s}" for s in strings]
    result = list(embedding_model.embed(strings))
    return result


def split_nomenclatures_by_chunks(
    nomenclatures: list[MappingOneNomenclatureUpload],
    chunk_size: int,
) -> list[list[MappingOneNomenclatureUpload]]:
    for i in range(0, len(nomenclatures), chunk_size):
        yield nomenclatures[i:i + chunk_size]


def create_mapping_job(
    nomenclatures: list[MappingOneNomenclatureUpload],
    most_similar_count: int,
    classifier_config: ClassifierConfig,
    tenant_id: int,
    iteration_key: str,
    previous_job_id: str | None = None,
) -> JobIdRead:
    queue = get_redis_queue(name=QueueName.MAPPING)
    job = queue.enqueue(
        _map_nomenclatures_chunk,
        nomenclatures,
        most_similar_count,
        classifier_config,
        tenant_id,
        iteration_key,
        meta={
            "previous_nomenclature_id": previous_job_id
        },
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT,
    )
    return JobIdRead(job_id=job.id)


def start_mapping(
    nomenclatures: list[MappingOneNomenclatureUpload],
    most_similar_count: int,
    chunk_size: int,
    classifier_config: ClassifierConfig,
    tenant_id: int,
    iteration_key: str | None = None,
) -> JobIdRead:
    # Check if collection name exists in user's classifier config
    collection_name = classifier_config.chroma_collection_name
    is_collection_name_exists_in_config = bool(collection_name)
    if not is_collection_name_exists_in_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Collection name is not set in classifier config.",
        )

    # Check if collection exists in vectorstore
    collections_list = get_all_collections()
    is_collection_exists_in_vectorstore = collection_name in collections_list
    if not is_collection_exists_in_vectorstore:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection {collection_name} is not exists in vectorstore.",
        )

    # Check if classifier version id exists in user's classifier config
    model_id = classifier_config.model_id
    is_model_id_exists_in_config = bool(model_id.strip())
    if not is_model_id_exists_in_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classifier version {model_id} is not exists.",
        )

    # Generate UUID for iteration
    if iteration_key is None:
        iteration_key = generate_uuid()

    # Split nomenclatures to chunks
    segments = split_nomenclatures_by_chunks(
        nomenclatures=nomenclatures,
        chunk_size=chunk_size,
    )
    last_job_id = None
    for segment in segments:
        job = create_mapping_job(
            nomenclatures=segment,
            previous_job_id=last_job_id,
            most_similar_count=most_similar_count,
            classifier_config=classifier_config,
            tenant_id=tenant_id,
            iteration_key=iteration_key,
        )
        last_job_id = job.job_id

    return JobIdRead(job_id=last_job_id)


def _map_nomenclatures_chunk(
    nomenclatures: list[MappingOneNomenclatureUpload],
    most_similar_count: int,
    classifier_config: ClassifierConfig,
    tenant_id: int,
    iteration_key: str,
) -> list[MappingOneNomenclatureRead]:
    logger.info(f"Classifier config for user with ID {classifier_config.user_id}: {classifier_config}")

    job = get_current_job()

    # Init job data
    job.meta['total_count'] = len(nomenclatures)
    job.meta['ready_count'] = 0
    job.save_meta()

    # Convert nomenclatures to DataFrame
    noms = convert_nomenclatures_to_df(nomenclatures)
    # Normalize nomenclatures names
    noms['normalized'] = noms['nomenclature'].progress_apply(
        lambda nom_name: normalize_name(nom_name)
    )

    # Extract nomenclature keyword
    is_use_keywords = classifier_config.is_use_keywords_detection
    if is_use_keywords:
        noms['keyword'] = noms['normalized'].progress_apply(
            lambda nom_name: extract_keyword(nom_name)
        )
    else:
        noms['keyword'] = None

    # Create embeddings for every mapping
    noms['embeddings'] = get_nomenclatures_embeddings(noms['nomenclature'].to_list())

    # Copy noms to "name" column for params extracting
    noms['name'] = noms['nomenclature']

    # Extract all noms params
    is_use_params = classifier_config.is_use_params
    if is_use_params:
        noms = extract_features(noms)

    # Get all noms brands
    is_use_brand_recognition = classifier_config.is_use_brand_recognition
    if is_use_brand_recognition:
        noms['brand'] = ner_service.predict(noms['nomenclature'].to_list())
    else:
        noms['brand'] = None

    # Run LLM to get nomenclatures views
    is_use_view_classification = classifier_config.is_use_view_classification
    if is_use_view_classification:
        noms = get_nomenclatures_views(noms)
    else:
        noms['view'] = None

    # Run classification to get nomenclatures groups
    model_id = classifier_config.model_id
    try:
        noms['internal_group'] = get_nomenclatures_groups(
            noms=noms,
            model_id=model_id,
            # is_use_params=is_use_params,
        )
    except ValueError:
        raise Exception(
            f"Model with ID '{model_id}' does not support params or DataFrame for prediction does not contains them"
        )

    # Get all noms params with group as metadatas list
    if is_use_params:
        noms['metadata'] = get_noms_metadatas_with_features(noms)
    else:
        noms['metadata'] = None

    collection_name = classifier_config.chroma_collection_name
    collection = connect_to_chroma_collection(collection_name)

    # Init noms result params
    noms['group'] = None
    noms['group_code'] = None
    noms['view_code'] = None
    noms['material_code'] = None
    noms['nomenclature_params'] = None
    noms['mappings'] = None
    noms['similar_mappings'] = None

    for i, nom in noms.iterrows():
        start_at = datetime.now()
        # Create mapping metadatas list for query
        if is_use_params:
            metadatas_list = []
            for key, val in nom['metadata'].items():
                # Check if mapping param is not empty
                if val != "":
                    metadatas_list.append({str(key): val})
        else:
            metadatas_list = None

        # Save metadatas in df for response
        nom['nomenclature_params'] = metadatas_list

        # Check if nom really belong to mapped group, only if is_use_keywords is True
        if is_use_keywords and nom['keyword'] not in nom['internal_group'].lower():
            nom['mappings'] = [MappingOneTargetRead(
                nomenclature_guid="",
                nomenclature="Для такой номенклатуры группы не нашлось",
                similarity_score=-1,
            )]
        else:
            # Map mapping with equal group and params
            mappings = map_on_nom(
                collection=collection,
                nom_embeddings=nom['embeddings'],
                group=nom['internal_group'],
                brand=nom['brand'],
                view=nom['view'],
                metadatas_list=metadatas_list,
                is_hard_params=True,
                is_use_params=is_use_params,
                is_use_brand_recognition=is_use_brand_recognition,
                is_use_view_classification=is_use_view_classification,
            )
            nom['mappings'] = mappings

            # Extract NSI group
            if mappings is not None:
                nom['group'] = _get_mappings_param("group", mappings)
                nom['group_code'] = _get_mappings_param("group_code", mappings)
                nom['view_code'] = _get_mappings_param("view_code", mappings)
                nom['material_code'] = _get_mappings_param("material_code", mappings)

            # Map similar nomenclatures if nom's params is not valid
            if mappings is None:
                similar_mappings = map_on_nom(
                    collection=collection,
                    nom_embeddings=nom['embeddings'],
                    group=nom['internal_group'],
                    brand=nom['brand'],
                    view=nom['view'],
                    metadatas_list=metadatas_list,
                    is_hard_params=False,
                    is_use_params=is_use_params,
                    is_use_brand_recognition=is_use_brand_recognition,
                    most_similar_count=most_similar_count,
                    is_use_view_classification=is_use_view_classification,
                )
                nom['similar_mappings'] = similar_mappings

                # Extract NSI group
                if similar_mappings is not None:
                    nom['group'] = _get_mappings_param("group", similar_mappings)
                    nom['group_code'] = _get_mappings_param("group_code", similar_mappings)
                    nom['view_code'] = _get_mappings_param("view_code", similar_mappings)
                    nom['material_code'] = _get_mappings_param("material_code", similar_mappings)

        noms.loc[i] = nom
        job.meta['ready_count'] += 1
        job.save_meta()

        end_at = datetime.now()
        logger.debug(f"Nomenclature processing time: {end_at - start_at}")

    job.meta['status'] = "finished"
    job.save_meta()

    noms['embeddings'] = None

    noms_dict = noms.to_dict(orient="records")
    result_nomenclatures = [MappingOneNomenclatureRead(**nom) for nom in noms_dict]

    # Save mapping results for feedback
    user_id = classifier_config.user_id
    save_mapping_result(
        nomenclatures=result_nomenclatures,
        user_id=user_id,
        iteration_key=iteration_key,
    )

    # Charge tenant used tokens for nomenclatures mapping
    tokens_count = count_used_tokens(result_nomenclatures)
    charge_used_tokens(
        tokens_count=tokens_count,
        tenant_id=tenant_id,
        user_id=user_id,
    )

    return result_nomenclatures


def get_jobs_from_rq(job_id: str) -> list[MappingNomenclaturesResultRead]:
    jobs_list: list[MappingNomenclaturesResultRead] = []

    prev_job_id = job_id
    while prev_job_id is not None:
        job = get_job(prev_job_id)
        job_meta = job.get_meta(refresh=True)
        job_status = job.get_status(refresh=True)
        job_result = MappingNomenclaturesResultRead(
            job_id=job.id,
            ready_count=job_meta.get("ready_count", None),
            total_count=job_meta.get("total_count", None),
            general_status=job_status,
        )

        if job_status == JobStatus.FINISHED:
            result_mappings: list[MappingOneNomenclatureRead] = job.return_value(refresh=True)
            job_result.nomenclatures = result_mappings

        jobs_list.append(job_result)
        prev_job_id = job_meta['previous_nomenclature_id']

    return jobs_list


def get_all_jobs(job_id: str) -> list[MappingNomenclaturesResultRead]:
    jobs_from_rq = get_jobs_from_rq(job_id)
    return jobs_from_rq


def is_job_finished(job_status: str) -> bool:
    if job_status == JobStatus.FINISHED:
        return True
    if job_status == JobStatus.FAILED:
        return True

    return False
