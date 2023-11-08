from fastapi import APIRouter, Depends, UploadFile
from fastapi_versioning import version

from dto.nomenclature_mapping_job_dto import NomenclatureMappingUpdateDto, NomenclatureMappingJobOutDto
from dto.user_dto import UserDto
from model import nomenclature_model
from service.auth_service import AuthService

router = APIRouter(
    prefix="/nomenclature",
    tags=["nomenclature"],
)


@router.get("/job/{source}", response_model=NomenclatureMappingJobOutDto)
@version(1)
def get_nomenclature_mapping_jobs(
    source: str | None = None,
    current_user: UserDto = Depends(AuthService.get_current_user)
):
    return nomenclature_model.get_all_jobs(source=source)


@router.put("")
@version(1)
def update_nomenclature_mapping(
    body: NomenclatureMappingUpdateDto,
    current_user: UserDto = Depends(AuthService.get_current_user)
):
    return nomenclature_model.update_nomenclature_mapping(body)


@router.post("/file")
@version(1)
def upload_file(
    file_object: UploadFile,
    current_user: UserDto = Depends(AuthService.get_current_user)
):
    return nomenclature_model.process(file_object)


if __name__ == "__main__":
    get_nomenclature_mapping_jobs()