import os

from postgrest import APIResponse
from supabase import Client, create_client


class SupabaseRepository:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def fetch_last_n_by_chat_id(self, chat_id: int, n: int) -> APIResponse:
        return self.supabase \
            .table("message") \
            .select("*, review(*)") \
            .eq("chat_id", chat_id) \
            .order("created_at", desc=True) \
            .limit(n) \
            .execute()


supabase_repository = SupabaseRepository()
