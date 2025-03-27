from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import time

from app.models.common import PaginatedResponse


class ResizeParams(BaseModel):
    """이미지 크기 조정 파라미터"""

    width: int
    height: int


class ProcessingRequest(BaseModel):
    """이미지 처리 요청 모델"""

    image_id: str
    resize: Optional[ResizeParams] = None
    filter: Optional[str] = None


class ImageUploadResponse(BaseModel):
    """이미지 업로드 응답 모델"""

    image_id: str
    filename: str
    size: int
    content_type: str
    status: str
    message: Optional[str] = None


class ImageMetadata(BaseModel):
    """이미지 메타데이터 모델"""

    image_id: str
    filename: str
    content_type: str
    size: int
    object_name: str
    upload_time: int
    status: str
    processing_requested: Optional[int] = None
    processing_params: Optional[Dict[str, Any]] = None
    processing_completed: Optional[int] = None
    processed_objects: Optional[List[str]] = None
    error: Optional[str] = None


class ProcessingResult(BaseModel):
    """처리 결과 모델"""

    image_id: str
    status: str
    message: str


class ImageListResponse(PaginatedResponse):
    """이미지 목록 응답 모델"""

    images: List[Dict[str, Any]]
