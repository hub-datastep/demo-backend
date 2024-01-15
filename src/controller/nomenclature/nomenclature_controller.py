import pathlib

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse
from fastapi_versioning import version

from dto.nomenclature_mapping_job_dto import NomenclatureMappingUpdateDto, NomenclatureMappingJobOutDto
from dto.user_dto import UserDto
from model import nomenclature_model
# from service.auth_service import AuthService

router = APIRouter()


@router.get("/job/{source}", response_model=list[NomenclatureMappingJobOutDto])
@version(1)
def get_nomenclature_mapping_jobs(
    source: str | None = None,
    # current_user: UserDto = Depends(AuthService.get_current_user)
):
    return nomenclature_model.get_all_jobs(source=source)


@router.put("")
@version(1)
def update_nomenclature_mapping(
    body: NomenclatureMappingUpdateDto,
    # current_user: UserDto = Depends(AuthService.get_current_user)
):
    return nomenclature_model.update_nomenclature_mapping(body)


@router.get("/file/{source}")
@version(1)
def get_file(
    source: str,
    # current_user: UserDto = Depends(AuthService.get_current_user)
):
    first_test_jobs = nomenclature_model.get_all_jobs(source)
    nomenclature_model.create_test_excel(
        nomenclature_model.transform_jobs_lists_to_dict([first_test_jobs])
    )
    filepath = f"{pathlib.Path(__file__).parent.resolve()}/../../data/sheet.xlsx"
    return FileResponse(filepath, media_type='application/octet-stream', filename="results.xlsx")


@router.post("/file")
@version(1)
def upload_file(
    file_object: UploadFile,
    # current_user: UserDto = Depends(AuthService.get_current_user)
):
    return nomenclature_model.process(file_object)


if __name__ == "__main__":
    get_nomenclature_mapping_jobs()
