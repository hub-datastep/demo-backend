from infra.supabase import supabase


class TenantRepository:
    @classmethod
    def get_db_uri_by_id(cls, tenant_id: int) -> str:
        (_, [tenant]), _ = supabase\
            .table("tenant")\
            .select("db_uri")\
            .eq("id", tenant_id)\
            .execute()
        return tenant["db_uri"]


tenant_repository = TenantRepository()
