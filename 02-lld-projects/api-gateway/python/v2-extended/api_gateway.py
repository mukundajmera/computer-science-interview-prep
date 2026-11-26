import re
from typing import Dict, List, Optional, Callable, Any
import time

class Request:
    def __init__(self, path: str, method: str, headers: Dict[str, str], body: Any = None):
        self.path = path
        self.method = method
        self.headers = headers
        self.body = body
        self.attributes: Dict[str, Any] = {}
        self.deadline_ms: int = 0
        self.is_cancelled: bool = False

class Response:
    def __init__(self, status_code: int, headers: Dict[str, str], body: Any):
        self.status_code = status_code
        self.headers = headers
        self.body = body

class Filter:
    def pre_filter(self, request: Request) -> Optional[Response]:
        pass
    def post_filter(self, response: Response) -> Response:
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
        
    def pre_filter(self, request: Request) -> Optional[Response]:
        client_id = request.headers.get("Client-ID", "unknown")
        now = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
            
        # Cleanup old requests
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
        
    def post_filter(self, response: Response) -> Response:
        # Assuming request context can be accessed, but here we just log response
        self.logs.append(f"Response code: {response.status_code}")
        return response

class Route:
    def __init__(self, prefix: str, target: str):
        self.prefix = prefix
        self.target = target

class ApiGateway:
    def __init__(self):
        self.routes: List[Route] = []
        self.filters: List[Filter] = []
        self.backends: Dict[str, Callable[[Request], Response]] = {}
    
    def add_route(self, prefix: str, target: str):
        self.routes.append(Route(prefix, target))
    
    def add_filter(self, filter: Filter):
        self.filters.append(filter)

    def register_backend(self, target: str, handler: Callable[[Request], Response]):
        self.backends[target] = handler

    def handle(self, request: Request) -> Response:
        if request.body is not None and len(str(request.body)) > 1024 * 1024:
            return Response(413, {}, "Payload Too Large")

        # 1. Execute Pre-filters
        filter_index = 0
        for filter in self.filters:
            response = filter.pre_filter(request)
            if response:
                return self._apply_post_filters(response, filter_index)
            filter_index += 1
        
        # 2. Route Matching
        matched_route = None
        for route in self.routes:
            if request.path.startswith(route.prefix):
                matched_route = route
                break
        
        last_index = len(self.filters)

        if not matched_route:
            return self._apply_post_filters(Response(404, {}, "Not Found"), last_index)
        
        # 3. Backend dispatching
        backend = self.backends.get(matched_route.target)
        if not backend:
            return self._apply_post_filters(Response(503, {}, "Service Unavailable"), last_index)

        if request.is_cancelled:
            return self._apply_post_filters(Response(499, {}, "Client Closed Request"), last_index)

        if request.deadline_ms > 0 and int(time.time() * 1000) > request.deadline_ms:
            return self._apply_post_filters(Response(504, {}, "Gateway Timeout"), last_index)

        is_idempotent = request.method.upper() == "GET" or "Idempotency-Key" in request.headers
        max_attempts = 2 if is_idempotent else 1

        for attempt in range(1, max_attempts + 1):
            try:
                backend_res = backend(request)
                if backend_res.status_code >= 500 and attempt < max_attempts:
                    continue
                return self._apply_post_filters(backend_res, last_index)
            except Exception as e:
                if attempt == max_attempts:
                    return self._apply_post_filters(Response(500, {}, "Internal Server Error"), last_index)

        return self._apply_post_filters(Response(500, {}, "Internal Server Error"), last_index)
            
    def _apply_post_filters(self, response: Response, start_index: int) -> Response:
        for i in range(start_index - 1, -1, -1):
            if i < len(self.filters):
                response = self.filters[i].post_filter(response)
        return response
