# app/llm/memory.py
import json
import redis.asyncio as redis

REDIS_URL = "redis://default:3LCFWUm8yrV4ZCPD0HI3vQDHIk9xM0EM@redis-19878.c8.us-east-1-2.ec2.cloud.redislabs.com:19878/0"


class AgentMemory:
    def __init__(self, chat_session_id: str):
        self.key = f"agent:chat:{chat_session_id}"
        self.redis = redis.from_url(REDIS_URL)

    async def append(self, role: str, content: str):
        await self.redis.rpush(
            self.key,
            json.dumps({"role": role, "content": content}),
        )
        await self.redis.expire(self.key, 3600)

    async def read(self, limit: int = 20):
        items = await self.redis.lrange(self.key, -limit, -1)
        return [json.loads(i) for i in items]

    async def clear(self):
        await self.redis.delete(self.key)
