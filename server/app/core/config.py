import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """애플리케이션 설정"""

    PROJECT_NAME: str = "Image Processing Service"
    API_V1_STR: str = "/api/v1"
    SERVICE_NAME: str = "image-processor"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Kafka 설정
    KAFKA_BOOTSTRAP_SERVERS: str = Field(
        default="kafka1:9092,kafka2:9093,kafka3:9094", env="KAFKA_BOOTSTRAP_SERVERS"
    )
    KAFKA_IMAGE_TOPIC: str = Field(
        default="image-processing-requests", env="KAFKA_IMAGE_TOPIC"
    )
    KAFKA_RESULT_TOPIC: str = Field(
        default="image-processing-results", env="KAFKA_RESULT_TOPIC"
    )

    # MinIO 설정
    MINIO_ENDPOINT: str = Field(default="minio:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="root-user", env="MINIO_SERVER_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(
        default="root-password", env="MINIO_SERVER_SECRET_KEY"
    )
    MINIO_SECURE: bool = Field(default=False, env="MINIO_SECURE")
    MINIO_ORIGINAL_BUCKET: str = Field(
        default="original-images", env="MINIO_ORIGINAL_BUCKET"
    )
    MINIO_PROCESSED_BUCKET: str = Field(
        default="processed-images", env="MINIO_PROCESSED_BUCKET"
    )

    # Elasticsearch 설정
    ELASTICSEARCH_HOST: str = Field(default="elasticsearch", env="ELASTICSEARCH_HOST")
    ELASTICSEARCH_PORT: int = Field(default=9200, env="ELASTICSEARCH_PORT")
    ELASTICSEARCH_INDEX: str = Field(default="images", env="ELASTICSEARCH_INDEX")

    # Redis 설정
    REDIS_HOST: str = Field(default="redis", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")

    # Spark 설정
    SPARK_MASTER: str = Field(default="spark://spark-master:7077", env="SPARK_MASTER")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
