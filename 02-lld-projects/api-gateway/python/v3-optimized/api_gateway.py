import re
import threading
from typing import Dict, List, Optional, Callable, Any
import time

class Request:
    def __init__(self, path: str, method: str, headers: Dict[str, str], body: Any = None):
        self.path = path
        self.method = method
        self.headers = headers
        self.body = body
        self.attributes: Dict[str, Any] = {}

class Response:
    def __init__(self, status_code: int, headers: Dict[str, str], body: Any):
        self.status_code = status_code
        self.headers = headers
        self.body = body

class Filter:
    def pre_filter(self, request: Request) -> Optional[Response]:
        pass
    def post_filter(self, request: Request, response: Response) -> Response:
        return response

class AuthFilter(Filter):
    def pre_filter(self, request: Request) -> Optional[Response]:
        if "Authorization" not in request.headers:
            return Response(401, {}, "Unauthorized")
        return None

class RateLimitFilter(Filter):
    def __init__(self, max_requests: int, window_sec: int):
        self.max_requests = max_requests
        self.window_sec = window_sec
        self.requests: Dict[str, List[float]] = {}
        self.client_locks: Dict[str, threading.Lock] = {}
        self.global_lock = threading.Lock()
        
    def pre_filter(self, request: Request) -> Optional[Response]:
        client_id = request.headers.get("Client-ID", "unknown")
        now = time.time()
        
        with self.global_lock:
            if client_id not in self.client_locks:
                self.client_locks[client_id] = threading.Lock()
            client_lock = self.client_locks[client_id]
            
        with client_lock:
            if client_id not in self.requests:
                self.requests[client_id] = []
                
            self.requests[client_id] = [t for t in self.requests[client_id] if now - t < self.window_sec]
            
            if len(self.requests[client_id]) >= self.max_requests:
                return Response(429, {}, "Too Many Requests")
                
            self.requests[client_id].append(now)
            
        return None

class LoggingFilter(Filter):
    def __init__(self):
        self.logs = []
        
    def pre_filter(self, request: Request) -> Optional[Response]:
        request.attributes["start_time"] = time.time()
        return None
        
    def post_filter(self, request: Request, response: Response) -> Response:
        duration = time.time() - request.attributes.get("start_time", time.time())
        self.logs.append(f"{request.method} {request.path} {response.status_code} {duration:.3f}s")
        return response

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, reset_timeout: int = 5):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0
        self.lock = threading.Lock()
        
    def allow_request(self) -> bool:
        with self.lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.reset_timeout:
                    self.state = "HALF_OPEN"
                    return True
                return False
            if self.state == "HALF_OPEN":
                return False
            return True
            
    def record_success(self):
        with self.lock:
            self.failures = 0
            self.state = "CLOSED"
            
    def record_failure(self):
        with self.lock:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
                self.last_failure_time = time.time()
            elif self.state == "HALF_OPEN":
                self.state = "OPEN"
                self.last_failure_time = time.time()

class Route:
    def __init__(self, prefix: str, target: str):
        self.prefix = prefix
        self.target = target

class ApiGateway:
    def __init__(self):
        self.routes: List[Route] = []
        self.filters: List[Filter] = []
        self.backends: Dict[str, Callable[[Request], Response]] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.lock = threading.Lock()
    
    def add_route(self, prefix: str, target: str):
        with self.lock:
            self.routes.append(Route(prefix, target))
            if target not in self.circuit_breakers:
                self.circuit_breakers[target] = CircuitBreaker()
            
    def add_filter(self, filter: Filter):
        with self.lock:
            self.filters.append(filter)

    def register_backend(self, target: str, handler: Callable[[Request], Response]):
        with self.lock:
            self.backends[target] = handler

    def handle(self, request: Request) -> Response:
        for filter in self.filters:
            response = filter.pre_filter(request)
            if response:
                return self._apply_post_filters(request, response)
        
        matched_route = None
        for route in self.routes:
            if request.path.startswith(route.prefix):
                matched_route = route
                break
        
        if not matched_route:
            return self._apply_post_filters(request, Response(404, {}, "Not Found"))
        
        cb = self.circuit_breakers.get(matched_route.target)
        if cb and not cb.allow_request():
            return self._apply_post_filters(request, Response(503, {}, "Service Unavailable - Circuit Open"))
            
        backend = self.backends.get(matched_route.target)
        if not backend:
            if cb:
                cb.record_failure()
            return self._apply_post_filters(request, Response(503, {}, "Service Unavailable"))
            
        try:
            backend_res = backend(request)
            if backend_res.status_code >= 500:
                if cb:
                    cb.record_failure()
            else:
                if cb:
                    cb.record_success()
            return self._apply_post_filters(request, backend_res)
        except Exception as e:
            if cb:
                cb.record_failure()
            return self._apply_post_filters(request, Response(500, {}, "Internal Server Error"))
            
    def _apply_post_filters(self, request: Request, response: Response) -> Response:
        for filter in reversed(self.filters):
            response = filter.post_filter(request, response)
        return response
