from repository.logo_repository import logo_repository
from repository.tenant_repository import tenant_repository
from constant.logo_default_path import LOGO_DEFAULT_PATH


def get_logo(user_id: str) -> str:
    tenant_id = tenant_repository.get_tenant_id_by_user_id(user_id)
    logo = logo_repository.fetch_logo_by_tenant_id(tenant_id)
    
    if logo is None:
        return LOGO_DEFAULT_PATH
    
    return logo
