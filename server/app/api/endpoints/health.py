from fastapi import APIRouter, Depends
from app.models.common import HealthResponse
from app.services.kafka.producer import get_kafka_producer
from app.services.storage.minio import get_minio_client
from app.db.elasticsearch.client import get_elasticsearch_client
from app.db.redis.client import get_redis_client

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    kafka=Depends(get_kafka_producer),
    minio=Depends(get_minio_client),
    elasticsearch=Depends(get_elasticsearch_client),
    redis=Depends(get_redis_client),
):
    """애플리케이션 상태 확인"""
    # 각 서비스별 연결 테스트 등 필요시 추가
    return {
        "status": "healthy",
        "services": {
            "api": "up",
            "kafka": "up",
            "minio": "up",
            "elasticsearch": "up",
            "redis": "up",
        },
    }
