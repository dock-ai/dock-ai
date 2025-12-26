"""Database layer for the registry - Supabase backend."""

import os
from functools import lru_cache

from supabase import create_client, Client


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Get a cached Supabase client instance."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError(
            "Missing Supabase credentials. "
            "Set SUPABASE_URL and SUPABASE_KEY environment variables."
        )

    return create_client(url, key)


def get_client() -> Client:
    """Get Supabase client (alias for consistency)."""
    return get_supabase_client()
