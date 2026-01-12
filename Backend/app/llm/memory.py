# app/llm/memory.py
import json
import redis.asyncio as redis

class AgentMemory:
    def __init__(self, user_id: str):
        self.key = f"agent:{user_id}"
        self.redis = redis.from_url("redis://localhost:6379")

    async def append(self, role: str, content: str):
        await self.redis.rpush(
            self.key,
            json.dumps({"role": role, "content": content}),
        )
        await self.redis.expire(self.key, 3600)

    async def read(self, limit=20):
        items = await self.redis.lrange(self.key, -limit, -1)
        return [json.loads(i) for i in items]

    async def clear(self):
        await self.redis.delete(self.key)
