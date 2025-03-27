from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from app.core.logging import get_logger

logger = get_logger("api.middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        request_id = request.headers.get("X-Request-Id", "-")
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"- ID: {request_id} - Client: {request.client.host}"
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            logger.info(
                f"Response: {request.method} {request.url.path}\n"
                f"- Status: {response.status_code}\n"
                f"- Process Time: {process_time:.4f}s\n"
                f"- ID: {request_id}\n"
            )

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"- Error: {str(e)} "
                f"- Process Time: {process_time:.4f}s "
                f"- ID: {request_id}"
            )

            # 예외 전파
            raise
