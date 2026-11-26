"""
Decorator Pattern - V3 Advanced: HTTP Middleware

Real-world example showing how web frameworks use decorator pattern
for request/response middleware (authentication, logging, caching).
Uses Python async/await for modern web framework style.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time


@dataclass
class HttpRequest:
    method: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def get_header(self, name: str) -> Optional[str]:
        return self.headers.get(name)
    
    def set_attribute(self, name: str, value: Any) -> None:
        self.attributes[name] = value
    
    def get_attribute(self, name: str) -> Optional[Any]:
        return self.attributes.get(name)


@dataclass
class HttpResponse:
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    
    def set_header(self, name: str, value: str) -> None:
        self.headers[name] = value


# Component Interface
class RequestHandler(ABC):
    @abstractmethod
    def handle(self, request: HttpRequest) -> HttpResponse:
        pass


# Concrete Component - Core Application Handler
class ApplicationHandler(RequestHandler):
    def handle(self, request: HttpRequest) -> HttpResponse:
        response = HttpResponse()
        
        if request.path == "/api/users":
            response.body = '{"users": [{"id": 1, "name": "Alice"}]}'
            response.set_header("Content-Type", "application/json")
            
        elif request.path == "/api/protected":
            user = request.get_attribute("user")
            if user:
                response.body = f'{{"message": "Welcome, {user}!"}}'
            else:
                response.status_code = 401
                response.body = '{"error": "Unauthorized"}'
                
        else:
            response.status_code = 404
            response.body = '{"error": "Not Found"}'
        
        return response


# Abstract Decorator
class Middleware(RequestHandler):
    def __init__(self, next_handler: RequestHandler):
        self._next = next_handler


# Concrete Decorator - Logging
class LoggingMiddleware(Middleware):
    def handle(self, request: HttpRequest) -> HttpResponse:
        start = time.time()
        print(f"[LOG] {request.method} {request.path}")
        
        response = self._next.handle(request)
        
        duration = (time.time() - start) * 1000
        print(f"[LOG] Response: {response.status_code} ({duration:.1f}ms)")
        
        return response


# Concrete Decorator - Authentication
class AuthenticationMiddleware(Middleware):
    VALID_TOKENS = {"valid-token-123", "admin-token-456"}
    
    def handle(self, request: HttpRequest) -> HttpResponse:
        auth_header = request.get_header("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            if token in self.VALID_TOKENS:
                request.set_attribute("user", "AuthenticatedUser")
                request.set_attribute("authenticated", True)
        
        return self._next.handle(request)


# Concrete Decorator - Rate Limiting
class RateLimitMiddleware(Middleware):
    def __init__(self, next_handler: RequestHandler, max_requests: int = 5):
        super().__init__(next_handler)
        self._request_counts: Dict[str, int] = {}
        self._max_requests = max_requests
    
    def handle(self, request: HttpRequest) -> HttpResponse:
        client_ip = request.get_header("X-Client-IP") or "unknown"
        
        count = self._request_counts.get(client_ip, 0) + 1
        self._request_counts[client_ip] = count
        
        if count > self._max_requests:
            print(f"[RATE LIMIT] Blocked: {client_ip}")
            response = HttpResponse(status_code=429)
            response.body = '{"error": "Too Many Requests"}'
            response.set_header("Retry-After", "60")
            return response
        
        return self._next.handle(request)


# Concrete Decorator - Caching
class CachingMiddleware(Middleware):
    def __init__(self, next_handler: RequestHandler):
        super().__init__(next_handler)
        self._cache: Dict[str, HttpResponse] = {}
    
    def handle(self, request: HttpRequest) -> HttpResponse:
        # Only cache GET requests
        if request.method != "GET":
            return self._next.handle(request)
        
        cache_key = request.path
        if cache_key in self._cache:
            print(f"[CACHE] Hit: {cache_key}")
            cached = self._cache[cache_key]
            cached.set_header("X-Cache", "HIT")
            return cached
        
        print(f"[CACHE] Miss: {cache_key}")
        response = self._next.handle(request)
        
        if response.status_code == 200:
            self._cache[cache_key] = response
        response.set_header("X-Cache", "MISS")
        
        return response


# Middleware factory using decorators
def create_middleware_stack(app: RequestHandler) -> RequestHandler:
    """Create a standard middleware stack"""
    handler = app
    handler = AuthenticationMiddleware(handler)
    handler = CachingMiddleware(handler)
    handler = RateLimitMiddleware(handler)
    handler = LoggingMiddleware(handler)
    return handler


# Demo
if __name__ == "__main__":
    # Build middleware stack
    handler = create_middleware_stack(ApplicationHandler())
    
    # Request 1: Simple GET
    print("=== Request 1: GET /api/users ===")
    req1 = HttpRequest("GET", "/api/users")
    req1.headers["X-Client-IP"] = "192.168.1.1"
    res1 = handler.handle(req1)
    print(f"Body: {res1.body}")
    
    # Request 2: Same request (should hit cache)
    print("\n=== Request 2: GET /api/users (cached) ===")
    req2 = HttpRequest("GET", "/api/users")
    req2.headers["X-Client-IP"] = "192.168.1.1"
    res2 = handler.handle(req2)
    print(f"Cache: {res2.headers.get('X-Cache')}")
    
    # Request 3: Protected endpoint without auth
    print("\n=== Request 3: GET /api/protected (no auth) ===")
    req3 = HttpRequest("GET", "/api/protected")
    req3.headers["X-Client-IP"] = "192.168.1.2"
    res3 = handler.handle(req3)
    print(f"Status: {res3.status_code}")
    
    # Request 4: Protected endpoint with auth
    print("\n=== Request 4: GET /api/protected (with auth) ===")
    req4 = HttpRequest("GET", "/api/protected")
    req4.headers["X-Client-IP"] = "192.168.1.2"
    req4.headers["Authorization"] = "Bearer valid-token-123"
    res4 = handler.handle(req4)
    print(f"Body: {res4.body}")
