from fastapi import APIRouter, Depends
from fastapi_versioning import version

from model import nomenclature_model
from model.auth_model import get_current_user
from scheme.nomenclature_scheme import JobIdRead, NomenclaturesUpload, NomenclaturesRead
from scheme.user_scheme import UserRead

router = APIRouter()


# @router.get("/job/{source}", response_model=list[NomenclatureMappingJobOutDto])
# @version(1)
# def get_nomenclature_mapping_jobs(
#     source: str | None = None,
#     # current_user: UserDto = Depends(AuthService.get_current_user)
# ):
#     return nomenclature_model.get_all_jobs(source=source)


# @router.put("")
# @version(1)
# def update_nomenclature_mapping(
#     body: NomenclatureMappingUpdateDto,
#     # current_user: UserDto = Depends(AuthService.get_current_user)
# ):
#     return nomenclature_model.update_nomenclature_mapping(body)


# @router.get("/file/{source}")
# @version(1)
# def get_file(
#     source: str,
#     # current_user: UserDto = Depends(AuthService.get_current_user)
# ):
#     first_test_jobs = nomenclature_model.get_all_jobs(source)
#     nomenclature_model.create_test_excel(
#         nomenclature_model.transform_jobs_lists_to_dict([first_test_jobs])
#     )
#     filepath = f"{pathlib.Path(__file__).parent.resolve()}/../../data/sheet.xlsx"
#     return FileResponse(filepath, media_type='application/octet-stream', filename="results.xlsx")


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

# if __name__ == "__main__":
#     get_nomenclature_mapping_jobs()
