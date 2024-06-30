from pathlib import Path

import joblib
import numpy as np
from chromadb import QueryResult
from chromadb.api.models.Collection import Collection
from fastembed import TextEmbedding
from pandas import DataFrame
from rq import get_current_job
from rq.job import JobStatus
from tqdm import tqdm

from infra.chroma_store import connect_to_chroma_collection
from infra.redis_queue import get_redis_queue, MAX_JOB_TIMEOUT, QueueName, get_job
from model.classifier.classifier_retrain_model import TRAINING_COLUMNS
from model.classifier.classifier_version_model import get_model_path
from scheme.classifier.classifier_config_scheme import ClassifierConfig
from scheme.mapping.mapping_scheme import MappingOneNomenclatureUpload, \
    MappingNomenclaturesResultRead, MappingOneTargetRead, MappingOneNomenclatureRead
from scheme.task.task_scheme import JobIdRead
from util.extract_keyword import extract_keyword
from util.features_extraction import extract_features, get_noms_metadatas_with_features
from util.normalize_name import normalize_name

tqdm.pandas()
# noinspection PyTypeChecker
np.set_printoptions(threshold=np.inf)

SIMILAR_NOMS_COUNT = 3


def get_nomenclatures_groups(
    noms: DataFrame,
    model_id: str,
    use_params: bool,
) -> list[int]:
    model_path = get_model_path(model_id)

    if not Path(model_path).exists():
        raise Exception(f"Model with ID {model_id} not found locally.")

    model = joblib.load(model_path)

    # If without params -> use only "normalized" column
    if use_params:
        final_training_columns = TRAINING_COLUMNS
    else:
        final_training_columns = TRAINING_COLUMNS[0]

    prediction_df = noms[final_training_columns]

    return model.predict(prediction_df)


def map_on_nom(
    collection: Collection,
    nom_embeddings: np.ndarray,
    group: str,
    most_similar_count: int,
    metadatas_list: list[dict],
    is_hard_params: bool,
    use_params: bool,
) -> list[MappingOneTargetRead] | None:
    # Just sure that group is str
    group = str(group)

    if len(metadatas_list) == 0 or not use_params:
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

    nom_embeddings = nom_embeddings.tolist()
    response: QueryResult = collection.query(
        query_embeddings=[nom_embeddings],
        where=where_metadatas,
        n_results=most_similar_count,
    )

    response_ids = response['ids'][0]
    response_documents = response['documents'][0]
    response_distances = response['distances'][0]

    if len(response_ids) == 0:
        return None

    mapped_noms = []
    for i in range(len(response_ids)):
        mapped_noms.append(MappingOneTargetRead(
            nomenclature_guid=response_ids[i],
            nomenclature=response_documents[i],
            similarity_score=response_distances[i],
        ))

    return mapped_noms


def convert_nomenclatures_to_df(nomenclatures: list[MappingOneNomenclatureUpload]) -> DataFrame:
    nomenclatures_as_json = [nom.dict().values() for nom in nomenclatures]
    return DataFrame(nomenclatures_as_json, columns=['row_number', 'mapping'])


def get_nomenclatures_embeddings(strings: list[str]) -> list[np.ndarray]:
    embedding_model = TextEmbedding(
        model_name="intfloat/multilingual-e5-large"
    )
    strings = [f"query: {s}" for s in strings]
    result = list(embedding_model.embed(strings))
    return result


def split_nomenclatures_by_chunks(
    nomenclatures: list[MappingOneNomenclatureUpload],
    chunk_size: int = 100,
) -> list[list[MappingOneNomenclatureUpload]]:
    # https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
    for i in range(0, len(nomenclatures), chunk_size):
        yield nomenclatures[i:i + chunk_size]


def create_mapping_job(
    nomenclatures: list[MappingOneNomenclatureUpload],
    previous_job_id: str | None,
    most_similar_count: int,
    chroma_collection_name: str,
    model_id: str,
    use_params: bool,
    classifier_config: ClassifierConfig | None,
) -> JobIdRead:
    queue = get_redis_queue(name=QueueName.MAPPING)
    job = queue.enqueue(
        _map_nomenclatures_chunk,
        nomenclatures,
        most_similar_count,
        chroma_collection_name,
        model_id,
        use_params,
        classifier_config,
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
    chroma_collection_name: str,
    chunk_size: int,
    model_id: str,
    use_params: bool,
    classifier_config: ClassifierConfig | None,
) -> JobIdRead:
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
            chroma_collection_name=chroma_collection_name,
            model_id=model_id,
            use_params=use_params,
            classifier_config=classifier_config,
        )
        last_job_id = job.job_id

    return JobIdRead(job_id=last_job_id)


def _map_nomenclatures_chunk(
    nomenclatures: list[MappingOneNomenclatureUpload],
    most_similar_count: int,
    chroma_collection_name: str,
    model_id: str,
    use_params: bool,
    classifier_config: ClassifierConfig | None,
) -> list[MappingOneNomenclatureRead]:
    job = get_current_job()

    # Convert nomenclatures to DataFrame
    noms = convert_nomenclatures_to_df(nomenclatures)

    job.meta['total_count'] = len(noms)
    job.meta['ready_count'] = 0
    job.save_meta()

    # Normalize nomenclatures names
    noms['normalized'] = noms['mapping'].progress_apply(
        lambda nom_name: normalize_name(nom_name)
    )

    is_use_keywords = classifier_config is None or classifier_config.is_use_keywords_detection

    if is_use_keywords:
        noms['keyword'] = noms['normalized'].progress_apply(
            lambda nom_name: extract_keyword(nom_name)
        )
    else:
        noms['keyword'] = None

    # Create embeddings for every mapping
    noms['embeddings'] = get_nomenclatures_embeddings(noms['mapping'].to_list())

    # Copy noms to name column for extracting features
    noms['name'] = noms['mapping']
    # Извлечение характеристик и добавление их в метаданные
    noms = extract_features(noms)

    # Classification to get mapping group
    noms['group'] = get_nomenclatures_groups(
        noms=noms,
        model_id=model_id,
        use_params=use_params,
    )

    # Получаем метаданные всех номенклатур с характеристиками
    noms['metadata'] = get_noms_metadatas_with_features(noms)

    collection = connect_to_chroma_collection(collection_name=chroma_collection_name)

    noms['mappings'] = None
    noms['similar_mappings'] = None
    noms['nomenclature_params'] = None
    for i, nom in noms.iterrows():
        # Create mapping metadatas list for query
        metadatas_list = []
        for key, val in nom['metadata'].items():
            # Check if mapping param is not empty
            if val != "":
                metadatas_list.append({str(key): val})

        nom['nomenclature_params'] = metadatas_list

        # Check if nom really belong to mapped group, only if is_use_keywords is True
        if is_use_keywords and nom['keyword'] not in nom['group'].lower():
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
                group=nom['group'],
                most_similar_count=most_similar_count,
                metadatas_list=metadatas_list,
                is_hard_params=True,
                use_params=use_params,
            )
            nom['mappings'] = mappings

            # Map similar nomenclatures if nom's params is not valid
            if mappings is None:
                similar_mappings = map_on_nom(
                    collection=collection,
                    nom_embeddings=nom['embeddings'],
                    group=nom['group'],
                    most_similar_count=SIMILAR_NOMS_COUNT,
                    metadatas_list=metadatas_list,
                    is_hard_params=False,
                    use_params=use_params,
                )
                nom['similar_mappings'] = similar_mappings

        noms.loc[i] = nom
        job.meta['ready_count'] += 1
        job.save_meta()

    job.meta['status'] = "finished"
    job.save_meta()

    noms['embeddings'] = None

    noms_dict = noms.to_dict(orient="records")
    result_nomenclatures = [MappingOneNomenclatureRead(**nom) for nom in noms_dict]

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
