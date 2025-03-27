from fastapi import HTTPException, status


class ImageProcessingException(HTTPException):
    """이미지 처리 관련 예외"""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "이미지 처리 중 오류가 발생했습니다",
    ):
        super().__init__(status_code=status_code, detail=detail)


class StorageException(HTTPException):
    """스토리지 관련 예외"""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "스토리지 작업 중 오류가 발생했습니다",
    ):
        super().__init__(status_code=status_code, detail=detail)


class KafkaException(HTTPException):
    """Kafka 관련 예외"""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "메시지 큐 작업 중 오류가 발생했습니다",
    ):
        super().__init__(status_code=status_code, detail=detail)


class ImageValidationException(HTTPException):
    """이미지 유효성 검증 예외"""

    def __init__(self, detail: str = "올바르지 않은 이미지 형식입니다"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )
