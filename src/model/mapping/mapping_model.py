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

tqdm.pandas()
# noinspection PyTypeChecker
np.set_printoptions(threshold=np.inf)


def get_nomenclatures_groups_old(
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
    # logger.info(f"model packages: {model_packages}")
    model = model_packages['model']
    label_encoder = model_packages['label_encoder']

    prediction_df = noms['nomenclature']
    prediction_list = prediction_df.to_list()

    # Predict groups ids and encode them to groups names
    predicted_groups = label_encoder.inverse_transform(
        model.predict(prediction_list)
    )

    return predicted_groups


def _build_where_metadatas_old(
    group: str,
    brand: str | None,
    metadatas_list: list[dict] | None,
    is_params_needed: bool,
    is_brand_needed: bool,
    is_hard_params: bool,
):
    if len(metadatas_list) == 0 or not is_params_needed:
        where_metadatas = {"$and": [
            {"group": group},
            {"brand": brand},
        ]}
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
    is_params_needed: bool,
    is_brand_needed: bool,
    is_hard_params: bool,
) -> Where:
    metadata_list_with_group = [
        {"internal_group": group},
        # Ставлю использование Вида номенклатуры пока здесь, пока у нас нет этого параметра в конфиге Классификатора
        {"view": view},
    ]
    # metadata_list_with_brand = [{"brand": brand}] if is_brand_needed else []
    # metadata_list_with_params = metadatas_list if is_params_needed else []
    metadata_list_with_brand = [{"brand": brand}]
    metadata_list_with_params = metadatas_list

    is_many_params = is_params_needed and len(metadata_list_with_params) > 1

    # If using hard-search
    # group, brand and params must be equal
    if is_hard_params:
        # If using params
        if is_params_needed:
            # If using brand
            if is_brand_needed:
                where_metadatas = {
                    "$and": [
                        *metadata_list_with_group,
                        *metadata_list_with_params,
                        *metadata_list_with_brand,
                    ],
                }

            # If not using brand
            else:
                where_metadatas = {
                    "$and": [
                        *metadata_list_with_group,
                        *metadata_list_with_params,
                    ],
                }

        # If not using params
        else:
            # If using brand
            if is_brand_needed:
                where_metadatas = {
                    "$and": [
                        *metadata_list_with_group,
                        *metadata_list_with_brand,
                    ],
                }

            # If not using brand
            else:
                # Where filter without view
                # where_metadatas = metadata_list_with_group[0]
                # Where filter with view
                where_metadatas = {
                    "$and": [
                        *metadata_list_with_group,
                    ],
                }

    # If using soft-search
    # group must be equal and any or nothing of brand and params is equal
    else:
        # If using params
        if is_params_needed:
            # If using brand
            if is_brand_needed:
                where_metadatas = {
                    "$and": [
                        *metadata_list_with_group,
                        {
                            "$or": [
                                *metadata_list_with_params,
                                *metadata_list_with_brand,
                            ],
                        },
                    ],
                }

            # If not using brand
            else:
                # If params 2 or more
                if is_many_params:
                    where_metadatas = {
                        "$and": [
                            *metadata_list_with_group,
                            {
                                "$or": [
                                    *metadata_list_with_params,
                                ],
                            },
                        ],
                    }

                # If is 1 param
                else:
                    where_metadatas = {
                        "$or": [
                            *metadata_list_with_group,
                            {
                                "$and": [
                                    *metadata_list_with_group,
                                    *metadata_list_with_params,
                                ],
                            },
                        ],
                    }

        # If not using params
        else:
            # If using brand
            if is_brand_needed:
                where_metadatas = {
                    "$or": [
                        *metadata_list_with_group,
                        {
                            "$and": [
                                *metadata_list_with_group,
                                *metadata_list_with_brand,
                            ],
                        },
                    ],
                }

            # If not using brand
            else:
                # Where filter without view
                # where_metadatas = metadata_list_with_group[0]
                # Where filter with view
                where_metadatas = {
                    "$and": [
                        *metadata_list_with_group,
                    ],
                }

    return where_metadatas


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
    most_similar_count: int = 1,
) -> list[MappingOneTargetRead] | None:
    is_params_exists = metadatas_list is not None and len(metadatas_list) > 0
    is_params_needed = is_params_exists and is_use_params

    is_brand_exists = brand is not None
    is_brand_needed = is_brand_exists and is_use_brand_recognition

    where_metadatas = build_where_metadatas(
        group=group,
        brand=brand,
        view=view,
        metadatas_list=metadatas_list,
        is_params_needed=is_params_needed,
        is_brand_needed=is_brand_needed,
        is_hard_params=is_hard_params,
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
        response_group = response_metadatas[i].get("group")
        mapped_noms.append(
            MappingOneTargetRead(
                nomenclature_guid=response_ids[i],
                nomenclature=response_documents[i],
                group=response_group,
                similarity_score=response_distances[i],
            )
        )

    return mapped_noms


def _get_mappings_group(mappings: list[MappingOneTargetRead]) -> str | None:
    mappings_group = None

    for mapping_nom in mappings:
        if mapping_nom is not None:
            mappings_group = mapping_nom.group
            break

    return mappings_group


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
    previous_job_id: str | None,
    most_similar_count: int,
    classifier_config: ClassifierConfig | None,
    tenant_id: int,
) -> JobIdRead:
    queue = get_redis_queue(name=QueueName.MAPPING)
    job = queue.enqueue(
        _map_nomenclatures_chunk,
        nomenclatures,
        most_similar_count,
        classifier_config,
        tenant_id,
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
    classifier_config: ClassifierConfig | None,
    tenant_id: int,
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
    is_model_id_exists_in_config = bool(model_id)
    if not is_model_id_exists_in_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classifier version {model_id} is not exists.",
        )

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
        )
        last_job_id = job.job_id

    return JobIdRead(job_id=last_job_id)


def _map_nomenclatures_chunk(
    nomenclatures: list[MappingOneNomenclatureUpload],
    most_similar_count: int,
    classifier_config: ClassifierConfig | None,
    tenant_id: int,
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
    is_use_keywords = classifier_config is None or classifier_config.is_use_keywords_detection
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

    # Get noms brand params
    is_use_brand_recognition = classifier_config is None or classifier_config.is_use_brand_recognition
    if is_use_brand_recognition:
        noms['brand'] = ner_service.predict(noms['nomenclature'].to_list())
    else:
        noms['brand'] = None
    # noms['brand'] = ner_service.predict(noms['nomenclature'].to_list())

    # Extract all noms params
    is_use_params = classifier_config is None or classifier_config.is_use_params
    if is_use_params:
        noms = extract_features(noms)

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

    # Run LLM to get nomenclatures views
    # TODO: add this to ClassifierConfig
    # TODO: run this only if param in ClassifierConfig is true
    noms = get_nomenclatures_views(noms)

    # Get all noms params with group as metadatas list
    if is_use_params:
        noms['metadata'] = get_noms_metadatas_with_features(noms)
    else:
        noms['metadata'] = None

    collection_name = classifier_config.chroma_collection_name
    collection = connect_to_chroma_collection(collection_name)

    # Init noms result params
    noms['group'] = None
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
            )
            nom['mappings'] = mappings

            # Extract NSI group
            if mappings is not None:
                nom['group'] = _get_mappings_group(mappings)

            # Map similar nomenclatures if nom's params is not valid
            if mappings is None:
                similar_mappings = map_on_nom(
                    collection=collection,
                    nom_embeddings=nom['embeddings'],
                    group=nom['internal_group'],
                    brand=nom['brand'],
                    view=nom['view'],
                    most_similar_count=most_similar_count,
                    metadatas_list=metadatas_list,
                    is_hard_params=False,
                    is_use_params=is_use_params,
                    is_use_brand_recognition=is_use_brand_recognition,
                )
                nom['similar_mappings'] = similar_mappings

                # Extract NSI group
                if similar_mappings is not None:
                    nom['group'] = _get_mappings_group(similar_mappings)

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
    )

    # Charge tenant used tokens for nomenclatures mapping
    tokens_count = count_used_tokens(result_nomenclatures)
    charge_used_tokens(
        tokens_count=tokens_count,
        tenant_id=tenant_id,
        user_id=user_id,
    )

    return result_nomenclatures


def get_jobs_from_rq(nomenclature_id: str) -> list[MappingNomenclaturesResultRead]:
    jobs_list: list[MappingNomenclaturesResultRead] = []

    prev_job_id = nomenclature_id
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


def get_all_jobs(nomenclature_id: str) -> list[MappingNomenclaturesResultRead]:
    jobs_from_rq = get_jobs_from_rq(nomenclature_id)
    return jobs_from_rq
