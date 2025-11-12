# import asyncio
# from supabase import create_client
# from django.conf import settings

# supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

# async def supabase_query(fn, *args, **kwargs):
#     """
#     Run Supabase queries in a thread pool to avoid blocking.
#     Example: await supabase_query(supabase.table("users").select("*").execute)
#     """
#     return await asyncio.to_thread(fn, *args, **kwargs)

import asyncio
import logging
from supabase import create_client
from django.conf import settings

logger = logging.getLogger(__name__)

_supabase = None

def get_supabase():
    """Lazy-load the Supabase client to ensure fresh config and safe reuse."""
    global _supabase
    if _supabase is None:
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _supabase

async def supabase_query(fn, *args, **kwargs):
    """
    Run Supabase queries in a thread pool to avoid blocking.
    Example:
        result = await supabase_query(
            get_supabase().table("users").select("*").execute
        )
    """
    try:
        return await asyncio.to_thread(fn, *args, **kwargs)
    except Exception as e:
        logger.error(f"Supabase query error: {e}")
        raise
