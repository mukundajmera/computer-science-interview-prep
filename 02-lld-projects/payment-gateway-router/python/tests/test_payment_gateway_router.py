import sys
import os
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from payment_request import PaymentRequest
from payment_response import PaymentResponse, PaymentStatus
from gateway_adapters import AbstractPaymentGateway
from router import GatewayRouter, HealthBasedRoutingStrategy
from idempotency_store import IdempotencyStore
from circuit_breaker import CircuitBreaker

class TestGateway(AbstractPaymentGateway):
    def __init__(self, name: str):
        super().__init__(name)
        self.succeed_next = True

    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        if not self.circuit_breaker.allow_request():
            return PaymentResponse(None, PaymentStatus.FAILED, "Circuit breaker open", self.name)

        if self.succeed_next:
            self.record_metrics(True)
            return PaymentResponse(f"txn-{self.name}", PaymentStatus.SUCCESS, "Success", self.name)
        else:
            self.record_metrics(False)
            return PaymentResponse(None, PaymentStatus.TIMEOUT, "Timeout", self.name)

class TestPaymentGatewayRouter(unittest.TestCase):
    def test_idempotency_deduplication(self):
        store = IdempotencyStore()
        strategy = HealthBasedRoutingStrategy()
        g1 = TestGateway("G1")
        router = GatewayRouter([g1], strategy, store)
        
        req1 = PaymentRequest("req1", "idem-1", 10.0, "USD", "u1")
        res1 = router.route_payment(req1)
        
        self.assertEqual(res1.status, PaymentStatus.SUCCESS)
        self.assertEqual(res1.gateway_name, "G1")
        
        req2 = PaymentRequest("req2", "idem-1", 10.0, "USD", "u1")
        res2 = router.route_payment(req2)
        
        self.assertEqual(res2.status, PaymentStatus.SUCCESS)
        self.assertEqual(res2.gateway_name, "G1")
        self.assertEqual(res1.transaction_id, res2.transaction_id)

    def test_health_based_routing(self):
        store = IdempotencyStore()
        strategy = HealthBasedRoutingStrategy()
        healthy = TestGateway("Healthy")
        unhealthy = TestGateway("Unhealthy")
        
        unhealthy.succeed_next = False
        unhealthy.process_payment(PaymentRequest("dummy", None, 10, "USD", "u"))
        
        router = GatewayRouter([unhealthy, healthy], strategy, store)
        req = PaymentRequest("req", "idem-2", 10.0, "USD", "u1")
        
        res = router.route_payment(req)
        
        self.assertEqual(res.gateway_name, "Healthy")

    def test_fallback_on_provider_timeout(self):
        store = IdempotencyStore()
        strategy = HealthBasedRoutingStrategy()
        primary = TestGateway("Primary")
        secondary = TestGateway("Secondary")
        
        primary.succeed_next = False
        
        router = GatewayRouter([primary, secondary], strategy, store)
        req = PaymentRequest("req", "idem-3", 10.0, "USD", "u1")
        
        res = router.route_payment(req)
        
        self.assertEqual(res.status, PaymentStatus.SUCCESS)
        self.assertEqual(res.gateway_name, "Secondary")

    def test_circuit_breaker_trip_and_reset(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout_ms=100)
        
        self.assertTrue(cb.allow_request())
        
        cb.record_failure()
        self.assertTrue(cb.allow_request())
        
        cb.record_failure()
        self.assertTrue(cb.allow_request())
        
        cb.record_failure()
        self.assertFalse(cb.allow_request())
        
        time.sleep(0.15)
        
        self.assertTrue(cb.allow_request())
        
        cb.record_success()
        self.assertTrue(cb.allow_request())

if __name__ == '__main__':
    unittest.main()
