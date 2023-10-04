from fastapi import HTTPException

from infra.supabase import supabase


class TenantRepository:
    @classmethod
    def get_db_uri_by_tenant_id(cls, tenant_id: int) -> str:
        (_, [tenant]), _ = supabase\
            .table("tenant")\
            .select("db_uri")\
            .eq("id", tenant_id)\
            .execute()
        return tenant["db_uri"]

    @classmethod
    def get_tenant_id_by_user_id(cls, user_id: str) -> int:
        (_, tenants_ids), _ = supabase\
            .table("user_tenant")\
            .select("tenant_id")\
            .eq("user_id", user_id)\
            .execute()

        if len(tenants_ids) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"User with id={user_id} does not belong to any tenant"
            )

        return tenants_ids[0]["tenant_id"]


tenant_repository = TenantRepository()
