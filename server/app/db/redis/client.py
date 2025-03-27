import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import get_logger
from typing import Any, Optional, Union, List, Dict

logger = get_logger(__name__)


class RedisClient:
    """Redis 클라이언트"""

    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,  # 문자열 응답 자동 디코딩
        )
        logger.info(
            f"Redis client initialized with host: {settings.REDIS_HOST}:{settings.REDIS_PORT}"
        )

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """값 설정"""
        try:
            await self.client.set(key, value)

            if expire:
                await self.client.expire(key, expire)

            logger.debug(f"Set Redis key: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to set Redis key {key}: {str(e)}")
            return False

    async def get(self, key: str) -> Optional[str]:
        """값 조회"""
        try:
            value = await self.client.get(key)
            return value

        except Exception as e:
            logger.error(f"Failed to get Redis key {key}: {str(e)}")
            return None

    async def delete(self, key: str) -> bool:
        """키 삭제"""
        try:
            await self.client.delete(key)
            logger.debug(f"Deleted Redis key: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete Redis key {key}: {str(e)}")
            return False

    async def hset(self, name: str, key: str, value: str) -> bool:
        """해시 필드 설정"""
        try:
            await self.client.hset(name, key, value)
            logger.debug(f"Set Redis hash field: {name}[{key}]")
            return True

        except Exception as e:
            logger.error(f"Failed to set Redis hash field {name}[{key}]: {str(e)}")
            return False

    async def hget(self, name: str, key: str) -> Optional[str]:
        """해시 필드 조회"""
        try:
            value = await self.client.hget(name, key)
            return value

        except Exception as e:
            logger.error(f"Failed to get Redis hash field {name}[{key}]: {str(e)}")
            return None

    async def hgetall(self, name: str) -> Dict[str, str]:
        """해시 모든 필드 조회"""
        try:
            values = await self.client.hgetall(name)
            return values

        except Exception as e:
            logger.error(f"Failed to get all Redis hash fields {name}: {str(e)}")
            return {}

    async def close(self):
        """클라이언트 연결 종료"""
        await self.client.close()


async def get_redis_client():
    """종속성 주입용 함수"""
    client = RedisClient()
    try:
        yield client
    finally:
        await client.close()
