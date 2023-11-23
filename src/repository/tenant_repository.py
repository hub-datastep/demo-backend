from fastapi import HTTPException

from sqlmodel import Session

from scheme.tenant_scheme import TenantCreate, Tenant


# from util.logger import log


def create_tenant(session: Session, tenant: TenantCreate) -> Tenant:
    tenant_db = Tenant.from_orm(tenant)
    session.add(tenant_db)
    session.commit()
    return tenant_db


# class TenantRepository:
#     @classmethod
#     # @log("Получение строки подключения к базе")
#     def get_db_uri_by_tenant_id(cls, tenant_id: int) -> str:
#         response = supabase\
#             .table("tenant")\
#             .select("db_uri")\
#             .eq("id", tenant_id)\
#             .execute()
#         return response.data[0]["db_uri"]
#
#     @classmethod
#     def get_tenant_id_by_user_id(cls, user_id: str) -> int:
#         response = supabase\
#             .table("user_tenant")\
#             .select("tenant_id")\
#             .eq("user_id", user_id)\
#             .execute()
#
#         if len(response.data) == 0:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"User with id={user_id} does not belong to any tenant"
#             )
#
#         return response.data[0]["tenant_id"]
#
#     @classmethod
#     def get_modes_by_tenant_id(cls, tenant_id: int) -> list[str]:
#         (_, modes), _ = supabase.table("mode_tenant").select("mode(*)").eq("tenant_id", tenant_id).execute()
#         return [entry["mode"]["name"] for entry in modes]
#
#
# tenant_repository = TenantRepository()


if __name__ == "__main__":
    print(TenantRepository.get_modes_by_tenant_id(3))