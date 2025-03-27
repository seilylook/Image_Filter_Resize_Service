import logging
import sys
from pydantic import BaseModel
from typing import Optional, Dict, Any


class LogConfig(BaseModel):
    """로깅 설정"""

    LOGGER_NAME: str = "image_processor"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "INFO"

    # 기본 로거 설정
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: Dict[str, Dict[str, str]] = {
        "default": {
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: Dict[str, Dict[str, Any]] = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            # 파일 객체 대신 문자열로 지정
            "stream": "ext://sys.stdout",
        },
    }
    loggers: Dict[str, Dict[str, Any]] = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
    }


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """로거 인스턴스 가져오기"""
    from logging.config import dictConfig

    config = LogConfig()
    # dictConfig를 사용하여 로깅 설정 적용
    dictConfig(config.model_dump())

    logger_name = name or config.LOGGER_NAME
    logger = logging.getLogger(logger_name)

    return logger
