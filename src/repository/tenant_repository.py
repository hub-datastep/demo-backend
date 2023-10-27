from fastapi import HTTPException

from infra.supabase import supabase
from dto.tenant_dto import TenantCreateDto, TenantDto


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
    def get_tenant_id_by_user_id(cls, user_id: str) -> int | None:
        (_, tenants_ids), _ = supabase\
            .table("user_tenant")\
            .select("tenant_id")\
            .eq("user_id", user_id)\
            .eq("is_last", True)\
            .execute()

        if len(tenants_ids) == 0:
            return None

        return tenants_ids[0]["tenant_id"]

    @classmethod
    def get_modes_by_tenant_id(cls, tenant_id: int) -> list[str]:
        (_, modes), _ = supabase.table("mode_tenant").select(
            "mode(*)").eq("tenant_id", tenant_id).execute()
        return [entry["mode"]["name"] for entry in modes]

    @classmethod
    def create_tenant(cls, body: TenantCreateDto) -> TenantDto:
        (_, [tenant]), _ = supabase\
            .table("tenant")\
            .insert(body.model_dump())\
            .execute()
        return TenantDto(**tenant)

    @classmethod
    def assign_user_id_to_tenant(cls, user_id: str, tenant_id: int):
        supabase\
            .table("user_tenant")\
            .insert({
                "user_id": user_id,
                "tenant_id": tenant_id,
                "is_last": True,
            })\
            .execute()

    @classmethod
    def assign_mode_to_tenant(cls, tenant_id: int):
        supabase\
            .table("mode_tenant")\
            .insert({
                "mode_id": 1,
                "tenant_id": tenant_id
            })\
            .execute()



tenant_repository = TenantRepository()


if __name__ == "__main__":
    print(TenantRepository.get_modes_by_tenant_id(3))
