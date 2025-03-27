from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from app.core.logging import get_logger
import io
import os
from typing import Optional, List, Dict, Any, Union

logger = get_logger(__name__)


class MinioService:
    """Minio 스토리지 서비스"""

    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

        self._ensure_buckets()
        logger.info(
            f"MinIO client initialized with endpoint: {settings.MINIO_ENDPOINT}"
        )

    def _ensure_buckets(self):
        """필요한 버킷 존재 확인 및 생성"""
        required_buckets = [
            settings.MINIO_ORIGINAL_BUCKET,
            settings.MINIO_PROCESSED_BUCKET,
        ]

        for bucket in required_buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"Bucket 생성 완료: {bucket}")
            except S3Error as e:
                logger.error(f"Error ensuring bucket {bucket}: {str(e)}")

    def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        file_data: Union[io.BytesIO, bytes],
        content_type: Optional[str] = None,
    ) -> bool:
        """파일 업로드"""
        try:
            # 파일 데이터 타입 처리
            if isinstance(file_data, bytes):
                file_data = io.BytesIO(file_data)
                file_size = len(file_data.getvalue())
            elif isinstance(file_data, io.BytesIO):
                file_size = file_data.getbuffer().nbytes
            else:
                logger.error(f"Unsupported file data type: {type(file_data)}")
                return False

            # 업로드
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type,
            )

            logger.debug(
                f"Uploaded file to {bucket_name}/{object_name} ({file_size} bytes)"
            )
            return True

        except S3Error as e:
            logger.error(f"Failed to upload file to MinIO: {str(e)}")
            return False

    def download_file(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """파일 다운로드"""
        try:
            # 객체 가져오기
            response = self.client.get_object(
                bucket_name=bucket_name, object_name=object_name
            )

            # 데이터 읽기
            data = response.read()
            response.close()
            response.release_conn()

            logger.debug(
                f"Downloaded file from {bucket_name}/{object_name} ({len(data)} bytes)"
            )
            return data

        except S3Error as e:
            logger.error(f"Failed to download file from MinIO: {str(e)}")
            return None

    def list_objects(
        self, bucket_name: str, prefix: Optional[str] = None, recursive: bool = True
    ) -> List[Dict[str, Any]]:
        """버킷 내 객체 목록 조회"""
        try:
            objects = self.client.list_objects(
                bucket_name=bucket_name, prefix=prefix, recursive=recursive
            )

            result = []
            for obj in objects:
                result.append(
                    {
                        "bucket_name": bucket_name,
                        "object_name": obj.object_name,
                        "size": obj.size,
                        "last_modified": obj.last_modified,
                        "etag": obj.etag,
                    }
                )

            return result

        except S3Error as e:
            logger.error(f"Failed to list objects in MinIO: {str(e)}")
            return []

    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        """파일 삭제"""
        try:
            self.client.remove_object(bucket_name=bucket_name, object_name=object_name)
            logger.debug(f"Deleted file {bucket_name}/{object_name}")
            return True

        except S3Error as e:
            logger.error(f"Failed to delete file from MinIO: {str(e)}")
            return False


def get_minio_client():
    """종속성 주입용 함수"""
    return MinioService()
