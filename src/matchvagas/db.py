import os

from supabase import Client, create_client


def get_client(admin: bool = False) -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"] if admin else os.environ["SUPABASE_ANON_KEY"]
    return create_client(url, key)
