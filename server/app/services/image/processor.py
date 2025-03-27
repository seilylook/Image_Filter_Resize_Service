import cv2
import numpy as np
import io
from typing import Dict, Any, Optional, Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)


class ImageProcessor:
    """서버 측 이미지 처리 서비스"""

    @staticmethod
    def resize_image(image_data: bytes, width: int, height: int) -> bytes:
        """이미지 크기 조정"""
        try:
            # 바이트 배열을 CV2 이미지로 변환
            image_array = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)

            # 이미지 크기 조정
            resized_img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

            # 처리된 이미지를 바이트 배열로 변환
            _, buffer = cv2.imencode(".jpg", resized_img)
            return buffer.tobytes()

        except Exception as e:
            logger.error(f"Failed to resize image: {str(e)}")

    @staticmethod
    def apply_filter(image_data: bytes, filter_type: str) -> bytes:
        """이미지 필터 적용"""
        try:
            # 바이트 배열을 CV2 이미지로 변환
            image_array = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            # 필터 적용
            if filter_type == "grayscale":
                filtered_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            elif filter_type == "blur":
                filtered_img = cv2.GaussianBlur(img, (15, 15), 0)
            elif filter_type == "edge":
                filtered_img = cv2.Canny(img, 100, 200)
            elif filter_type == "sepia":
                # 세피아 필터 행렬
                sepia_kernel = np.array(
                    [
                        [0.272, 0.534, 0.131],
                        [0.349, 0.686, 0.168],
                        [0.393, 0.769, 0.189],
                    ]
                )
                filtered_img = cv2.transform(img, sepia_kernel)
            else:
                # 기본값: 원본 이미지 반환
                return image_data

            # 처리된 이미지를 바이트 배열로 변환
            if len(filtered_img.shape) == 2:  # 흑백 이미지인 경우
                _, buffer = cv2.imencode(".jpg", filtered_img)
            else:
                _, buffer = cv2.imencode(".jpg", filtered_img)

            return buffer.tobytes()

        except Exception as e:
            logger.error(f"Failed to apply filter {filter_type}: {str(e)}")
            return image_data

    @staticmethod
    def get_image_info(image_data: bytes) -> Dict[str, Any]:
        """이미지 정보 추출"""
        try:
            # 바이트 배열을 CV2 이미지로 변환
            image_array = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)

            # 이미지 크기
            height, width = img.shape[:2]

            # 채널 수
            channels = 1 if len(img.shape) == 2 else img.shape[2]

            # 이미지 타입
            depth = img.dtype

            return {
                "width": width,
                "height": height,
                "channels": channels,
                "depth": str(depth),
                "size_bytes": len(image_data),
            }

        except Exception as e:
            logger.error(f"Failed to get image info: {str(e)}")
            return {"error": str(e)}
