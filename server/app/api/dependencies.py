from fastapi import Depends, Header, HTTPException, status
from typing import Optional
from app.services.kafka.producer import KafkaProducerService, get_kafka_producer
from app.services.storage.minio import MinioService, get_minio_client
from app.db.elasticsearch.client import ElasticsearchClient, get_elasticsearch_client
from app.db.redis.client import RedisClient, get_redis_client


def validate_content_type(content_type: Optional[str] = Header(None)) -> str:
    """콘텐츠 타입 검증"""
    if content_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content-Type 헤더가 필요합니다.",
        )

    # 이미지 업로드 시 multipart-form-data 체크
    if not content_type.startswith("multipart/form-data"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Content-Type은 multipart/form-data여야 합니다.",
        )

    return content_type


def get_services(
    kafka_producer: KafkaProducerService = Depends(get_kafka_producer),
    minio_client: MinioService = Depends(get_minio_client),
    es_client: ElasticsearchClient = Depends(get_elasticsearch_client),
    redis_client: RedisClient = Depends(get_redis_client),
):
    """모든 서비스 종속성"""
    return {
        "kafka_producer": kafka_producer,
        "minio_client": minio_client,
        "es_client": es_client,
        "redis_client": redis_client,
    }
