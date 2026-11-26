import unittest
import time
from v3.gateway_v3 import GatewayV3, BackendService

class MockFailingBackend(BackendService):
    def __init__(self, name, fail_count):
        super().__init__(name)
        self.fail_count = fail_count
        self.calls = 0

    def call(self, timeout=None):
        self.calls += 1
        if self.calls <= self.fail_count:
            raise TimeoutError("Simulated timeout")
        return f"{self.name} success"

class MockSuccessBackend(BackendService):
    def call(self, timeout=None):
        return f"{self.name} success"

class TestGatewayV3(unittest.TestCase):
    def test_successful_request(self):
        gateway = GatewayV3()
        backend = MockSuccessBackend("auth")
        res = gateway.handle(backend, 1.0)
        self.assertEqual(res, "auth success")

    def test_retry_success(self):
        # Allow 100% retries for test
        gateway = GatewayV3(retry_budget=1.0)
        # Fails once, succeeds on retry
        backend = MockFailingBackend("payment", fail_count=1)
        res = gateway.handle(backend, 1.0)
        self.assertEqual(res, "payment success")
        self.assertEqual(backend.calls, 2)

    def test_retry_budget_exhausted(self):
        gateway = GatewayV3(retry_budget=0.0) # No retries allowed
        backend = MockFailingBackend("payment", fail_count=1)
        res = gateway.handle(backend, 1.0)
        self.assertEqual(res, "504 Gateway Timeout")
        self.assertEqual(backend.calls, 1) # No second call made

    def test_circuit_breaker_opens(self):
        gateway = GatewayV3(retry_budget=0.0)
        backend = MockFailingBackend("inventory", fail_count=5)
        
        # 3 failures should open the breaker
        self.assertEqual(gateway.handle(backend, 1.0), "504 Gateway Timeout")
        self.assertEqual(gateway.handle(backend, 1.0), "504 Gateway Timeout")
        self.assertEqual(gateway.handle(backend, 1.0), "504 Gateway Timeout")
        
        # 4th request should fail fast (503)
        self.assertEqual(gateway.handle(backend, 1.0), "503 Service Unavailable (Circuit Breaker OPEN)")
        self.assertEqual(backend.calls, 3) # Backend not called on 4th attempt

    def test_aggregation(self):
        gateway = GatewayV3()
        b1 = MockSuccessBackend("user")
        b2 = MockFailingBackend("cart", fail_count=10) # will always timeout
        
        res = gateway.aggregate([b1, b2], 1.0)
        
        self.assertEqual(res["user"], "user success")
        self.assertEqual(res["cart"], "504 Gateway Timeout")

if __name__ == '__main__':
    unittest.main()
