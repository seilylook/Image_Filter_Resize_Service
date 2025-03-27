from pydantic import BaseModel
from typing import Dict, Any, Optional, List


class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""

    status: str
    services: Dict[str, str]


class PaginatedResponse(BaseModel):
    """페이지네이션 응답 기본 모델"""

    total: int
    page: int
    limit: int


class ErrorResponse(BaseModel):
    """오류 응답 모델"""

    detail: str
    code: Optional[str] = None
    path: Optional[str] = None
