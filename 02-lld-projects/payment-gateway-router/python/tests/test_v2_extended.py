import sys
import os
import time
import pytest

# Remove previously loaded modules so we load v2-extended
if 'router' in sys.modules: del sys.modules['router']
if 'gateway_adapters' in sys.modules: del sys.modules['gateway_adapters']
if 'idempotency_store' in sys.modules: del sys.modules['idempotency_store']
if 'payment_request' in sys.modules: del sys.modules['payment_request']
if 'payment_response' in sys.modules: del sys.modules['payment_response']
if 'circuit_breaker' in sys.modules: del sys.modules['circuit_breaker']

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from payment_request import PaymentRequest
from payment_response import PaymentResponse, PaymentStatus
from gateway_adapters import AbstractPaymentGateway
from router import GatewayRouter, DynamicMetricsRoutingStrategy
from idempotency_store import IdempotencyStore

class MyTestGateway(AbstractPaymentGateway):
    def __init__(self, name: str, simulated_latency: float = 0.0):
        super().__init__(name)
        self.succeed_next = True
        self.simulated_latency = simulated_latency

    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        if not self.circuit_breaker.allow_request():
            return PaymentResponse(None, PaymentStatus.FAILED, "Circuit breaker open", self.name)

        if self.succeed_next:
            self.record_metrics(True, self.simulated_latency)
            return PaymentResponse(f"txn-{self.name}", PaymentStatus.SUCCESS, "Success", self.name)
        else:
            self.record_metrics(False, self.simulated_latency)
            return PaymentResponse(None, PaymentStatus.TIMEOUT, "Timeout", self.name)

def test_dynamic_routing_by_success_rate():
    store = IdempotencyStore()
    strategy = DynamicMetricsRoutingStrategy()
    
    g1 = MyTestGateway("G1") # 100% success rate initially
    g2 = MyTestGateway("G2")
    
    # Make G2 fail once to drop its success rate
    g2.succeed_next = False
    g2.process_payment(PaymentRequest("dummy", None, 10, "USD", "u"))
    
    router = GatewayRouter([g1, g2], strategy, store)
    req = PaymentRequest("req", "idem-2", 10.0, "USD", "u1")
    
    res = router.route_payment(req)
    
    assert res.gateway_name == "G1"

def test_dynamic_routing_by_latency():
    store = IdempotencyStore()
    strategy = DynamicMetricsRoutingStrategy()
    
    g1 = MyTestGateway("G1", simulated_latency=50.0)
    g2 = MyTestGateway("G2", simulated_latency=20.0)
    
    # Seed metrics
    g1.process_payment(PaymentRequest("dummy1", None, 10, "USD", "u"))
    g2.process_payment(PaymentRequest("dummy2", None, 10, "USD", "u"))
    
    router = GatewayRouter([g1, g2], strategy, store)
    req = PaymentRequest("req", "idem-3", 10.0, "USD", "u1")
    
    res = router.route_payment(req)
    
    # G2 has lower latency and same success rate
    assert res.gateway_name == "G2"

def test_fallback_on_provider_timeout_v2():
    store = IdempotencyStore()
    strategy = DynamicMetricsRoutingStrategy()
    primary = MyTestGateway("Primary")
    secondary = MyTestGateway("Secondary")
    
    primary.succeed_next = False
    
    router = GatewayRouter([primary, secondary], strategy, store)
    req = PaymentRequest("req", "idem-4", 10.0, "USD", "u1")
    
    res = router.route_payment(req)
    
    assert res.status == PaymentStatus.SUCCESS
    assert res.gateway_name == "Secondary"

def test_all_gateways_fail_v2():
    store = IdempotencyStore()
    strategy = DynamicMetricsRoutingStrategy()
    g1 = MyTestGateway("G1")
    g2 = MyTestGateway("G2")
    
    g1.succeed_next = False
    g2.succeed_next = False
    
    router = GatewayRouter([g1, g2], strategy, store)
    req = PaymentRequest("req", "idem-5", 10.0, "USD", "u1")
    
    res = router.route_payment(req)
    
    assert res.status in (PaymentStatus.FAILED, PaymentStatus.TIMEOUT)

def test_circuit_breaker_trips_v2():
    store = IdempotencyStore()
    strategy = DynamicMetricsRoutingStrategy()
    g1 = MyTestGateway("G1")
    
    g1.succeed_next = False
    for _ in range(3):
        g1.process_payment(PaymentRequest("dummy", None, 10, "USD", "u"))
        
    router = GatewayRouter([g1], strategy, store)
    req = PaymentRequest("req", "idem-6", 10.0, "USD", "u1")
    
    res = router.route_payment(req)
    assert res.status in (PaymentStatus.FAILED, PaymentStatus.TIMEOUT)
    assert "unavailable" in res.message
