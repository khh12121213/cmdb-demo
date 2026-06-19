import asyncio
from app.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB

import redis.asyncio as aioredis

_redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD or None,
            db=REDIS_DB,
            decode_responses=True,
        )
    return _redis_pool


async def acquire_lock(env_code: str, app_code: str, group_code: str, trace_id: str, ttl_seconds: int = 3600) -> bool:
    """
    发布锁：SET NX EX，兼容Redis 5.0+
    锁Key: lock:deploy:{env}:{app}:{group}
    锁Value: trace_id
    """
    r = await get_redis()
    key = f"lock:deploy:{env_code}:{app_code}:{group_code}"
    ok = await r.set(key, trace_id, nx=True, ex=ttl_seconds)
    return bool(ok)


async def release_lock(env_code: str, app_code: str, group_code: str, trace_id: str) -> bool:
    """释放锁，校验trace_id防止误删"""
    r = await get_redis()
    key = f"lock:deploy:{env_code}:{app_code}:{group_code}"
    # Lua脚本保证原子性
    script = """
    if redis.call("GET", KEYS[1]) == ARGV[1] then
        return redis.call("DEL", KEYS[1])
    else
        return 0
    end
    """
    result = await r.eval(script, 1, key, trace_id)
    return int(result) == 1


async def check_lock(env_code: str, app_code: str, group_code: str) -> dict:
    """查询当前锁状态"""
    r = await get_redis()
    key = f"lock:deploy:{env_code}:{app_code}:{group_code}"
    trace_id = await r.get(key)
    ttl = await r.ttl(key) if trace_id else 0
    return {"locked": trace_id is not None, "trace_id": trace_id, "ttl_seconds": ttl}
