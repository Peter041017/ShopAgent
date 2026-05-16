import time
import uuid
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = str(uuid.uuid4())[:8]
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request %s failed path=%s", rid, request.url.path)
            raise
        dur = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s %s -> %s %.1fms",
            rid,
            request.method,
            request.url.path,
            getattr(response, "status_code", "?"),
            dur,
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简化的内存速率限制中间件（单进程可用，生产环境建议用 Redis）"""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clients: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # 仅限制 chat 相关接口
        if not request.url.path.startswith("/api/v1/chat"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = self._clients[client_ip]
        # 移除窗口外的记录
        self._clients[client_ip] = [t for t in window if now - t < self.window_seconds]

        if len(self._clients[client_ip]) >= self.max_requests:
            logger.warning("rate limit exceeded for %s", client_ip)
            return Response(status_code=429, content="请求过于频繁，请稍后再试")

        self._clients[client_ip].append(now)
        return await call_next(request)
