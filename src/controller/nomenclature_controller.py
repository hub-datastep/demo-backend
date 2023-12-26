import os

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse
from fastapi_versioning import version

from dto.nomenclature_mapping_job_dto import NomenclatureMappingUpdateDto, NomenclatureMappingJobDto
from dto.user_dto import UserDto
from model import nomenclature_model
from service.auth_service import AuthService

router = APIRouter(
    prefix="/nomenclature",
    tags=["nomenclature"],
)


@router.get("/job/{source}", response_model=list[NomenclatureMappingJobDto])
@version(1)
def get_nomenclature_mapping_jobs(
    source: str | None = None,
    current_user: UserDto = Depends(AuthService.get_current_user)
):
    return nomenclature_model.get_all_jobs(source=source)


@router.get("/file/{source}")
@version(1)
def get_file(
    source: str,
    current_user: UserDto = Depends(AuthService.get_current_user)
):
    return FileResponse(
        f"{os.getcwd()}/data/{source.replace('.txt', '')}_result.csv",
        media_type="application/octet-stream",
        filename="results.csv"
    )


@router.post("/file")
@version(1)
def upload_file(
    file_object: UploadFile,
    current_user: UserDto = Depends(AuthService.get_current_user)
):
    return nomenclature_model.create_job(file_object)


if __name__ == "__main__":
    get_nomenclature_mapping_jobs()
