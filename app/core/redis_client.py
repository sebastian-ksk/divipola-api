import redis
import json
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def get_cache(key: str) -> Optional[dict]:
    """Obtiene datos del cache"""
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None


def set_cache(key: str, value: dict, expire: int = 3600):
    """Guarda datos en el cache"""
    redis_client.setex(key, expire, json.dumps(value, default=str))


def delete_cache(pattern: str):
    """Elimina keys del cache que coincidan con el patrón"""
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)

