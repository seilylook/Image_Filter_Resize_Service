from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import uuid

from app.api.endpoints import health, images
from app.api.middlewares.logging import LoggingMiddleware
from app.core.config import settings
from app.core.exceptions import (
    ImageProcessingException,
    StorageException,
    KafkaException,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="이미지 크기 조정 및 필터링 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_prefix="/openapi.json",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
