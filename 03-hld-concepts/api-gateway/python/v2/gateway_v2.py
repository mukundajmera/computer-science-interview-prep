import time
import hmac
import hashlib

class Filter:
    def execute(self, request):
        pass

class AuthFilter(Filter):
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode('utf-8')

    def execute(self, request):
        token = request.get("token")
        if not token:
            return "401 Unauthorized"
        
        # Simple HMAC token verification
        # Expected token format: payload.signature
        parts = token.split(".")
        if len(parts) != 2:
            return "401 Unauthorized"
        
        payload, signature = parts
        expected_sig = hmac.new(self.secret_key, payload.encode('utf-8'), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(expected_sig, signature):
            return "401 Unauthorized"
        return None

class RateLimitFilter(Filter):
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def execute(self, request):
        now = time.time()
        # Refill tokens
        time_passed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return None
        else:
            return "429 Too Many Requests"

class GatewayV2:
    def __init__(self):
        self.filters = []

    def add_filter(self, filter_obj: Filter):
        self.filters.append(filter_obj)

    def handle(self, request):
        for f in self.filters:
            err = f.execute(request)
            if err:
                return err
        return f"200 OK -> {request.get('path')}"
