from repository.tenant_repository import tenant_repository
from constant.logo_default_path import LOGO_DEFAULT_PATH
from constant.db_uri_default_path import DB_URI_DEFAULT_PATH
from dto.tenant_dto import TenantCreateDto, TenantDto


def create_tenant_with_user_id(user_id: str):

    tenant_id = tenant_repository.get_tenant_id_by_user_id(user_id)

    if tenant_id == None:
        new_tenant = tenant_repository.create_tenant(
            TenantCreateDto(
                name="new tenant",
                logo=LOGO_DEFAULT_PATH,
                db_uri=DB_URI_DEFAULT_PATH,
            )
        )
        tenant_repository.assign_user_id_to_tenant(user_id, new_tenant.id)
