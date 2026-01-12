# app/services/cache_service.py
from app.core.redis import redis_client
import json


async def cache_order_status(order_id, status):
    await redis_client.set(f"order:{order_id}:status", status, ex=300)


async def get_cached_order_status(order_id):
    val = await redis_client.get(f"order:{order_id}:status")
    return val
