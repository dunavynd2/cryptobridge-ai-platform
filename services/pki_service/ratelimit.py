import threading
import time
from collections import defaultdict, deque
from typing import Awaitable, Callable, Deque, Dict

from fastapi import Request, Response
from starlette.responses import JSONResponse

_WINDOW_SECONDS = 60
_MAX_REQUESTS_PER_WINDOW = 120

_lock = threading.Lock()
_hits: Dict[str, Deque[float]] = defaultdict(deque)


async def rate_limit_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Simple in-memory fixed-window limiter keyed by API key (or client IP)."""
    client_id = request.headers.get("x-api-key") or (request.client.host if request.client else "anonymous")
    now = time.monotonic()
    with _lock:
        hits = _hits[client_id]
        while hits and now - hits[0] > _WINDOW_SECONDS:
            hits.popleft()
        if len(hits) >= _MAX_REQUESTS_PER_WINDOW:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        hits.append(now)
    return await call_next(request)
