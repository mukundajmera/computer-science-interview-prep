"""v2-variant: Chain of Responsibility Pattern for HTTP Middleware Pipelines.

Demonstrates web request processing with authentication, rate limiting, and input sanitization,
allowing early short-circuiting when filters fail.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional


class HttpRequest:
    def __init__(self, path: str, token: Optional[str], body: Optional[str], client_ip: str) -> None:
        self.path: str = path
        self.token: Optional[str] = token
        self.body: Optional[str] = body
        self.client_ip: str = client_ip


class HttpResponse:
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code: int = status_code
        self.message: str = message

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300


class Middleware(ABC):
    def __init__(self) -> None:
        self._next: Optional[Middleware] = None

    def link_with(self, next_middleware: "Middleware") -> "Middleware":
        self._next = next_middleware
        return next_middleware

    @abstractmethod
    def handle(self, request: HttpRequest) -> HttpResponse:
        pass

    def check_next(self, request: HttpRequest) -> HttpResponse:
        if self._next is None:
            return HttpResponse(200, "OK: Request processed successfully")
        return self._next.handle(request)


class AuthMiddleware(Middleware):
    def handle(self, request: HttpRequest) -> HttpResponse:
        if not request.token or not request.token.startswith("Bearer "):
            return HttpResponse(401, "Unauthorized: Missing or invalid bearer token")
        return self.check_next(request)


class RateLimitMiddleware(Middleware):
    def __init__(self, max_per_minute: int) -> None:
        super().__init__()
        self._max = max_per_minute
        self._counts: Dict[str, int] = {}

    def handle(self, request: HttpRequest) -> HttpResponse:
        ip = request.client_ip
        current = self._counts.get(ip, 0) + 1
        self._counts[ip] = current
        if current > self._max:
            return HttpResponse(429, "Too Many Requests: Rate limit exceeded")
        return self.check_next(request)


class SanitizationMiddleware(Middleware):
    def handle(self, request: HttpRequest) -> HttpResponse:
        if request.body and "<script>" in request.body:
            return HttpResponse(400, "Bad Request: Malicious script tags detected")
        return self.check_next(request)
