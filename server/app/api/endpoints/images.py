from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
    BackgroundTasks,
    Response,
)
from fastapi.responses import StreamingResponse
from typing import List, Optional
import uuid
import io
import time
from app.core.config import settings
from app.core.logging import get_logger
from app.models.image import (
    ImageUploadResponse,
    ProcessingRequest,
    ImageMetadata,
    ProcessingResult,
    ImageListResponse,
)
from app.services.storage.minio import MinioService, get_minio_client
from app.services.kafka.producer import KafkaProducerService, get_kafka_producer
from app.services.image.validation import validate_image_file
from app.db.elasticsearch.client import ElasticsearchClient, get_elasticsearch_client
from app.db.redis.client import RedisClient, get_redis_client
from app.core.exceptions import StorageException, ImageValidationException

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    minio_client: MinioService = Depends(get_minio_client),
    kafka_producer: KafkaProducerService = Depends(get_kafka_producer),
    es_client: ElasticsearchClient = Depends(get_elasticsearch_client),
):
    """원본 이미지 업로드 엔드포인트"""
    try:
        content = await file.read()
        validate_image_file(content, file.filename)
    except ImageValidationException as e:
        logger.e(f"이미지 유효성 검증 실패: {str(e)}")
    finally:
        await file.seek(0)

    image_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1].lower()
    object_name = f"{image_id}.{file_extension}"

    file_content = await file.read()
    content_type = file.content_type or "application/octet-stream"

    upload_success = minio_client.upload_file(
        buck_name=settings.MINIO_ORIGINAL_BUCKET,
        object_name=object_name,
        file_data=io.BytesIO(file_content),
        content_type=content_type,
    )

    if not upload_success:
        raise StorageException(detail="이미지 업로드에 실패했습니다.")

    metadata = {
        "image_id": image_id,
        "filename": file.filename,
        "content_type": content_type,
        "size": len(file_content),
        "object_name": object_name,
        "upload_time": int(time.time()),
        "status": "uploaded",
    }

    background_tasks.add_task(
        es_client.index_document,
        index_name=settings.ELASTICSEARCH_INDEX,
        document=metadata,
        doc_id=image_id,
    )

    return {
        "image_id": image_id,
        "filename": file.filename,
        "size": len(file_content),
        "content_type": content_type,
        "status": "uploaded",
        "message": "이미지가 성공적으로 업로드되었습니다",
    }


@router.post("/process", response_model=ProcessingResult)
async def process_image(
    request: ProcessingRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    kafka_producer: KafkaProducerService = Depends(get_kafka_producer),
    es_client: ElasticsearchClient = Depends(get_elasticsearch_client),
):
    """이미지 처리 요청 엔드포인트"""
    image_exists = await es_client.get_document(
        index_name=settings.ELASTICSEARCH_INDEX,
        doc_id=request.image_id,
    )

    if not image_exists:
        raise HTTPException(
            status_code=404, detail=f"이미지를 찾을 수 없습니다: {request.image_id}"
        )

    message = {
        "image_id": request.image_id,
        "bucket": settings.MINIO_ORIGINAL_BUCKET,
        "object_name": f"{request.image_id}.{image_exists.get('filename', '').split('.')[-1]}",
        "params": {
            "width": str(request.resize.width) if request.resize else None,
            "height": str(request.resize.height) if request.resize else None,
            "filter": request.filter,
        },
    }

    message_sent = kafka_producer.send_message(
        topic=settings.KAFKA_IMAGE_TOPIC,
        key=request.image_id,
        value=message,
    )

    if not message_sent:
        raise HTTPException(
            status_code=500, detail="처리 요청을 Kafka 큐에 전송하지 못했습니다."
        )

    processing_metadata = {
        "processing_requested": int(time.time()),
        "processing_params": {
            "resize": request.resize.dict() if request.resize else None,
            "filter": request.filter,
        },
        "status": "processing",
    }

    background_tasks.add_task(
        es_client.update_document,
        indx_name=settings.ELASTICSEARCH_INDEX,
        doc_id=request.image_id,
        document=processing_metadata,
    )

    return {
        "image_id": request.image_id,
        "status": "processing",
        "message": "이미지 처리 요청이 성공적으로 전송되었습니다.",
    }


@router.get("/{image_id}", response_model=ImageMetadata)
async def get_image_metadata(
    image_id: str, es_client: ElasticsearchClient = Depends(get_elasticsearch_client)
):
    """이미지 메타데이터 조회"""
    metadata = await es_client.get_document(
        index_name=settings.ELASTICSEARCH_INDEX, doc_id=image_id
    )

    if not metadata:
        raise HTTPException(
            status_code=404, detail=f"이미지를 찾을 수 없습니다: {image_id}"
        )

    return metadata


@router.get("/{image_id}/download")
async def download_processed_image(
    image_id: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    filter_type: Optional[str] = None,
    minio_client: MinioService = Depends(get_minio_client),
    es_client: ElasticsearchClient = Depends(get_elasticsearch_client),
):
    """처리된 이미지 다운로드"""
    metadata = await es_client.get_document(
        index_name=settings.ELASTICSEARCH_INDEX, doc_id=image_id
    )

    if not metadata:
        raise HTTPException(
            status_code=404, detail=f"이미지를 찾을 수 없습니다: {image_id}"
        )

    filter_name = filter_type or "original"
    width_str = str(width) if width else "orig"
    height_str = str(height) if height else "orig"

    processed_object = f"{image_id}/{filter_name}_{width_str}x{height_str}.jpg"

    image_data = minio_client.download_file(
        bucket_name=settings.MINIO_PROCESSED_BUCKET,
        object_name=processed_object,
    )

    if not image_data:
        # 처리된 이미지가 없다면 원본 반환
        image_data = minio_client.download_file(
            bucket_name=settings.MINIO_ORIGINAL_BUCKET,
            object_name=f"{image_id}.{metadata.get('filename', '').split('.')[-1]}",
        )

        if not image_data:
            raise HTTPException(status_code=404, detail="이미지를 찾을 수 없습니다.")

    return StreamingResponse(
        io.BytesIO(image_data), media_type=metadata.get("content_type", "image/jpeg")
    )


@router.get("", response_model=ImageListResponse)
async def list_images(
    page: int = 1,
    limit: int = 20,
    es_client: ElasticsearchClient = Depends(get_elasticsearch_client),
):
    """이미지 목록 조회"""
    from_ = (page - 1) * limit

    result = await es_client.search_documents(
        index_name=settings.ELASTICSEARCH_INDEX,
        query={"match_all": {}},
        from_=from_,
        size=limit,
        sort=[{"upload_time": {"order": "desc"}}],
    )

    total = result.get("total", {}).get("value", 0)
    images = result.get("hits", [])

    return {"total": total, "page": page, "limit": limit, "images": images}
