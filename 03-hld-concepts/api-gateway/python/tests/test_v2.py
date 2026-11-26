import unittest
import hmac
import hashlib
import time
from v2.gateway_v2 import GatewayV2, AuthFilter, RateLimitFilter

class TestGatewayV2(unittest.TestCase):
    def setUp(self):
        self.gateway = GatewayV2()
        self.secret = "my-secret"
        self.gateway.add_filter(AuthFilter(self.secret))
        self.gateway.add_filter(RateLimitFilter(capacity=2, refill_rate=0.0))

    def generate_token(self, payload):
        sig = hmac.new(self.secret.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()
        return f"{payload}.{sig}"

    def test_missing_token(self):
        res = self.gateway.handle({"path": "/api"})
        self.assertEqual(res, "401 Unauthorized")

    def test_invalid_token(self):
        res = self.gateway.handle({"path": "/api", "token": "user1.bad_sig"})
        self.assertEqual(res, "401 Unauthorized")

    def test_valid_token(self):
        token = self.generate_token("user1")
        res = self.gateway.handle({"path": "/api", "token": token})
        self.assertEqual(res, "200 OK -> /api")

    def test_rate_limiting(self):
        token = self.generate_token("user1")
        req = {"path": "/api", "token": token}
        
        # Request 1 (Success)
        self.assertEqual(self.gateway.handle(req), "200 OK -> /api")
        # Request 2 (Success)
        self.assertEqual(self.gateway.handle(req), "200 OK -> /api")
        # Request 3 (Rate Limited)
        self.assertEqual(self.gateway.handle(req), "429 Too Many Requests")

if __name__ == '__main__':
    unittest.main()
