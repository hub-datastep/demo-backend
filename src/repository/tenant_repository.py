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
        response = supabase\
            .table("user_tenant")\
            .select("tenant_id")\
            .eq("user_id", user_id)\
            .eq("is_last", True)\
            .execute()

        if len(response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"User with id={user_id} does not belong to any tenant"
            )

        return response.data[0]["tenant_id"]

    @classmethod
    def get_modes_by_tenant_id(cls, tenant_id: int) -> list[str]:
        (_, modes), _ = supabase.table("mode_tenant").select("mode(*)").eq("tenant_id", tenant_id).execute()
        return [entry["mode"]["name"] for entry in modes]


tenant_repository = TenantRepository()


if __name__ == "__main__":
    print(TenantRepository.get_modes_by_tenant_id(3))