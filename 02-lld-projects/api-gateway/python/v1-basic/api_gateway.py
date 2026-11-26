import re
from typing import Dict, List, Optional, Callable, Any

import time

class Request:
    def __init__(self, path: str, method: str, headers: Dict[str, str], body: Any = None):
        self.path = path
        self.method = method
        self.headers = headers
        self.body = body
        self.deadline_ms: int = 0
        self.is_cancelled: bool = False
        self.attributes: Dict[str, Any] = {}

class Response:
    def __init__(self, status_code: int, headers: Dict[str, str], body: Any):
        self.status_code = status_code
        self.headers = headers
        self.body = body

class Filter:
    def filter(self, request: Request) -> Optional[Response]:
        pass

class AuthFilter(Filter):
    def filter(self, request: Request) -> Optional[Response]:
        if "Authorization" not in request.headers:
            return Response(401, {}, "Unauthorized")
        return None

class Route:
    def __init__(self, prefix: str, target: str):
        self.prefix = prefix
        self.target = target

class ApiGateway:
    def __init__(self):
        self.routes: List[Route] = []
        self.pre_filters: List[Filter] = []
        self.backends: Dict[str, Callable[[Request], Response]] = {}
    
    def add_route(self, prefix: str, target: str):
        self.routes.append(Route(prefix, target))
    
    def add_pre_filter(self, filter: Filter):
        self.pre_filters.append(filter)

    def register_backend(self, target: str, handler: Callable[[Request], Response]):
        self.backends[target] = handler

    def handle(self, request: Request) -> Response:
        if request.body is not None and len(str(request.body)) > 1024 * 1024:
            return Response(413, {}, "Payload Too Large")

        # 1. Execute Pre-filters
        for filter in self.pre_filters:
            response = filter.filter(request)
            if response:
                return response
        
        # 2. Route Matching
        matched_route = None
        for route in self.routes:
            if request.path.startswith(route.prefix):
                matched_route = route
                break
        
        if not matched_route:
            return Response(404, {}, "Not Found")
        
        # 3. Backend dispatching
        backend = self.backends.get(matched_route.target)
        if not backend:
            return Response(503, {}, "Service Unavailable")
            
        if request.is_cancelled:
            return Response(499, {}, "Client Closed Request")
            
        if request.deadline_ms > 0 and int(time.time() * 1000) > request.deadline_ms:
            return Response(504, {}, "Gateway Timeout")
            
        is_idempotent = request.method.upper() == "GET" or "Idempotency-Key" in request.headers
        max_attempts = 2 if is_idempotent else 1
        
        for attempt in range(1, max_attempts + 1):
            try:
                res = backend(request)
                if res.status_code >= 500 and attempt < max_attempts:
                    continue
                return res
            except Exception as e:
                if attempt == max_attempts:
                    return Response(500, {}, "Internal Server Error")
                    
        return Response(500, {}, "Internal Server Error")
