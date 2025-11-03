import asyncio
from supabase import create_client
from django.conf import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

async def supabase_query(fn, *args, **kwargs):
    """
    Run Supabase queries in a thread pool to avoid blocking.
    Example: await supabase_query(supabase.table("users").select("*").execute)
    """
    return await asyncio.to_thread(fn, *args, **kwargs)
