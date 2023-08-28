import os

from dotenv import load_dotenv
from postgrest import APIResponse
from supabase import Client, create_client

from datastep.models.test import Test
from datastep.models.test_set import TestSet


load_dotenv()


class SupabaseRepository:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def insert_test(self, test: Test) -> APIResponse:
        return self.supabase.table("test").insert(test.get_obj()).execute()

    def insert_test_set(self, test_set: TestSet) -> APIResponse:
        return self.supabase.table("test_set").insert(test_set.get_obj()).execute()

    # TODO: Разобраться, как положить в API Reponse TestSetDto: APIResponse<TestSetDto>
    def select_test_sets(self) -> APIResponse:
        return self.supabase.table("test_set").select("*").execute()

    def select_test_by_test_set_id(self, test_set_id) -> APIResponse:
        return self.supabase.table("test").select("*").eq("test_id", test_set_id).execute()


supabase_repository = SupabaseRepository()
