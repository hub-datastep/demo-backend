from fastapi import HTTPException

from infra.supabase import supabase


class UserTenantRepository:
    @classmethod
    def get_tenant_id_by_user_id(cls, user_id: str) -> int:
        (_, tenants_ids), _ = supabase\
            .table("user_tenant")\
            .select("tenant_id")\
            .eq("user_id", user_id)\
            .execute()

        if len(tenants_ids) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"Tenant with user_id={user_id} does not exist."
            )

        return tenants_ids[0]["tenant_id"]


user_tenant_repository = UserTenantRepository()
