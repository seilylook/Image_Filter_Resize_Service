import io
from typing import Optional, Tuple
import imghdr
from PIL import Image
from app.core.logging import get_logger
from app.core.exceptions import ImageValidationException

logger = get_logger(__name__)

# 지원되는 이미지 형식
SUPPORTED_FORMATS = {"jpeg", "jpg", "png", "gif", "bmp", "webp"}
# 최대 이미지 크기 (20MB)
MAX_IMAGE_SIZE = 20 * 1024 * 1024
# 최대 이미지 해상도
MAX_RESOLUTION = 8000 * 8000


def validate_image_file(
    file_content: bytes, filename: Optional[str] = None
) -> Tuple[bool, str]:
    """이미지 파일 유효성 검증"""
    # 파일 크기 검사
    file_size = len(file_content)
    if file_size > MAX_IMAGE_SIZE:
        logger.warning(f"Image too large: {file_size} bytes (max: {MAX_IMAGE_SIZE})")
        raise ImageValidationException(
            detail=f"이미지 파일 크기가 너무 큽니다. 최대 20MB까지 허용됩니다."
        )

    # 이미지 형식 검사
    image_format = imghdr.what(None, h=file_content)
    if not image_format:
        logger.warning(f"Unknown image format for file: {filename}")
        raise ImageValidationException(detail="알 수 없는 이미지 형식입니다.")

    if image_format.lower() not in SUPPORTED_FORMATS:
        logger.warning(f"Unsupported image format: {image_format}")
        raise ImageValidationException(
            detail=f"지원되지 않는 이미지 형식입니다. 지원 형식: {', '.join(SUPPORTED_FORMATS)}"
        )

    # 이미지 해상도 검증
    try:
        with Image.open(io.BytesIO(file_content)) as img:
            width, height = img.size
            resolution = width * height

            if resolution > MAX_RESOLUTION:
                logger.warning(f"Image resolution too high: {width} x {height}")
                raise ImageValidationException(
                    detail=f"이미지 해상도가 너무 높습니다. 최대 8000x8000까지 허용됩니다."
                )
    except Exception as e:
        logger.error(f"Failed to open image: {str(e)}")
        raise ImageValidationException(detail="이미지 파일을 처리할 수 없습니다.")

    return True, image_format
