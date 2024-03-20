from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi_versioning import version

from model import nomenclature_model, noms2embeddings_model, synchronize_embeddings_model
from model.auth_model import get_current_user
from scheme.nomenclature_scheme import JobIdRead, NomenclaturesUpload, NomenclaturesRead, CreateAndSaveEmbeddings, \
    SyncNomenclatures
from scheme.user_scheme import UserRead

router = APIRouter()


@router.get("/{job_id}", response_model=list[NomenclaturesRead])
@version(1)
def get_nomenclature_mappings(
    *,
    current_user: UserRead = Depends(get_current_user),
    job_id: str
):
    return nomenclature_model.get_all_jobs(job_id)


@router.post("", response_model=JobIdRead)
@version(1)
def upload_nomenclature(
    *,
    current_user: UserRead = Depends(get_current_user),
    nomenclatures: NomenclaturesUpload
):
    return nomenclature_model.start_mapping(nomenclatures)


@router.post("/collection/{collection_name}")
@version(1)
def create_chroma_collection(
    *,
    current_user: UserRead = Depends(get_current_user),
    collection_name: str
):
    return noms2embeddings_model.create_chroma_collection(collection_name=collection_name)


@router.get("/collection/{collection_name}")
@version(1)
def get_chroma_collection_length(
    *,
    current_user: UserRead = Depends(get_current_user),
    collection_name: str
):
    return noms2embeddings_model.get_chroma_collection_length(collection_name=collection_name)


@router.delete("/collection/{collection_name}")
@version(1)
def delete_chroma_collection(
    *,
    current_user: UserRead = Depends(get_current_user),
    collection_name: str
):
    return noms2embeddings_model.delete_chroma_collection(collection_name=collection_name)


@router.put("/collection")
@version(1)
def create_and_save_embeddings(
    *,
    current_user: UserRead = Depends(get_current_user),
    body: CreateAndSaveEmbeddings,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        noms2embeddings_model.create_and_save_embeddings,
        nom_db_con_str=body.nom_db_con_str,
        table_name=body.table_name,
        top_n=body.top_n,
        order_by=body.order_by,
        offset=body.offset,
        chroma_collection_name=body.chroma_collection_name
    )
    return


@router.put("/synchronize")
@version(1)
def synchronize_embeddings(
    *,
    body: SyncNomenclatures,
    current_user: UserRead = Depends(get_current_user),
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        synchronize_embeddings_model.synchronize_embeddings,
        nom_db_con_str=body.nom_db_con_str,
        table_name=body.table_name,
        chroma_collection_name=body.chroma_collection_name,
        sync_period=body.sync_period
    )
    return
