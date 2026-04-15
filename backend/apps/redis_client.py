import logging
import redis
from django.conf import settings

logger = logging.getLogger(__name__)

_redis_client = None


def get_redis_client():
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            _redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            _redis_client = None
    return _redis_client


def redis_available():
    client = get_redis_client()
    if client is None:
        return False
    try:
        client.ping()
        return True
    except Exception:
        return False
