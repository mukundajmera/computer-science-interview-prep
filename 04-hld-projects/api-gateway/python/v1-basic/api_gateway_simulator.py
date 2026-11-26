class Request:
    def __init__(self, path, headers):
        self.path = path
        self.headers = headers

class Response:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body

class CircuitBreaker:
    def __init__(self):
        self.state = "CLOSED"
        self.failure_count = 0
        self.threshold = 3

    def allow_request(self):
        if self.state == "OPEN":
            return False
        return True

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.threshold:
            self.state = "OPEN"

    def trip_open(self):
        self.state = "OPEN"
        
    def reset(self):
        self.state = "CLOSED"
        self.failure_count = 0

class ApiGatewaySimulator:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()

    def handle_request(self, request):
        # 1. Security/Auth Filter
        if not request.headers or "Authorization" not in request.headers:
            return Response(401, "Unauthorized")
            
        # 2. Circuit Breaker Filter
        if not self.circuit_breaker.allow_request():
            return Response(503, "Service Unavailable")
            
        # 3. Routing/Proxy (Simulation)
        # If we made it here in normal trace, simulate success
        self.circuit_breaker.record_success()
        return Response(200, "OK from downstream")

