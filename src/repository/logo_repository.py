from infra.supabase import supabase

class LogoRepository:
    @classmethod
    def fetch_logo_by_tenant_id(cls, tenant_id: int) -> str:
        (_, logo), _ = supabase\
            .table("tenant")\
            .select("logo")\
            .eq("id", tenant_id)\
            .execute()

        return logo[0]["logo"] 

logo_repository = LogoRepository()
