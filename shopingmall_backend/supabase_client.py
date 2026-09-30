import os

from dotenv import load_dotenv
from supabase import Client, create_client


def get_supabase_client() -> Client:
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

    if not url or not publishable_key:
        raise RuntimeError(
            "SUPABASE_URL과 SUPABASE_PUBLISHABLE_KEY를 .env에 설정하세요."
        )

    return create_client(url, publishable_key)
