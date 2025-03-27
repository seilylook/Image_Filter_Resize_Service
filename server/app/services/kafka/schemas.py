from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class ImageProcessingRequest(BaseModel):
    """이미지 처리 요청 메시지"""

    image_id: str
    bucket: str
    object_name: str
    params: Dict[str, Optional[str]] = Field(default_factory=dict)


class ImageProcessingResult(BaseModel):
    """이미지 처리 결과 메시지"""

    image_id: str
    original_bucket: str
    original_object: str
    processed_bucket: str
    processed_object: str
    processing_time: float
    params: Dict[str, Any] = Field(default_factory=dict)
    status: str = "completed"
    error: Optional[str] = None
