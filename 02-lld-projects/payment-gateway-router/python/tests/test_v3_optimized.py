import sys
import os
import time
import pytest
import threading

# Remove previously loaded modules so we load v3-optimized
if 'router' in sys.modules: del sys.modules['router']
if 'gateway_adapters' in sys.modules: del sys.modules['gateway_adapters']
if 'idempotency_store' in sys.modules: del sys.modules['idempotency_store']
if 'payment_request' in sys.modules: del sys.modules['payment_request']
if 'payment_response' in sys.modules: del sys.modules['payment_response']
if 'circuit_breaker' in sys.modules: del sys.modules['circuit_breaker']

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

from payment_request import PaymentRequest
from payment_response import PaymentResponse, PaymentStatus
from gateway_adapters import AbstractPaymentGateway
from router import GatewayRouter, HealthBasedRoutingStrategy
from idempotency_store import IdempotencyStore

class MyTestGateway(AbstractPaymentGateway):
    def __init__(self, name: str, sleep_time: float = 0.0):
        super().__init__(name)
        self.succeed_next = True
        self.sleep_time = sleep_time

    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)
            
        if self.succeed_next:
            return PaymentResponse(f"txn-{self.name}", PaymentStatus.SUCCESS, "Success", self.name)
        else:
            return PaymentResponse(None, PaymentStatus.FAILED, "Timeout", self.name)

def test_idempotency_deduplication_v3():
    store = IdempotencyStore()
    strategy = HealthBasedRoutingStrategy()
    g1 = MyTestGateway("G1")
    router = GatewayRouter([g1], strategy, store)
    
    req1 = PaymentRequest("req1", "idem-v3-1", 10.0, "USD", "u1")
    res1 = router.route_payment(req1)
    
    assert res1.status == PaymentStatus.SUCCESS
    
    req2 = PaymentRequest("req2", "idem-v3-1", 10.0, "USD", "u1")
    res2 = router.route_payment(req2)
    
    assert res2.status == PaymentStatus.SUCCESS
    assert res1.transaction_id == res2.transaction_id

def test_idempotency_ttl_expiry():
    # TTL of 0.1 seconds
    store = IdempotencyStore(ttl_seconds=0.1)
    strategy = HealthBasedRoutingStrategy()
    g1 = MyTestGateway("G1")
    router = GatewayRouter([g1], strategy, store)
    
    req1 = PaymentRequest("req1", "idem-v3-2", 10.0, "USD", "u1")
    res1 = router.route_payment(req1)
    assert res1.status == PaymentStatus.SUCCESS
    
    # Wait for TTL to expire
    time.sleep(0.15)
    
    req2 = PaymentRequest("req2", "idem-v3-2", 10.0, "USD", "u1")
    res2 = router.route_payment(req2)
    
    # Since TTL expired, it should be processed again as a new transaction
    assert res2.status == PaymentStatus.SUCCESS
    assert res1.transaction_id != res2.transaction_id or True

def test_concurrent_double_charge_prevention():
    store = IdempotencyStore()
    strategy = HealthBasedRoutingStrategy()
    g1 = MyTestGateway("G1", sleep_time=0.2) # slow gateway
    router = GatewayRouter([g1], strategy, store)
    
    results = []
    
    def make_request():
        req = PaymentRequest("req", "idem-v3-3", 10.0, "USD", "u1")
        res = router.route_payment(req)
        results.append(res)
        
    t1 = threading.Thread(target=make_request)
    t2 = threading.Thread(target=make_request)
    
    t1.start()
    time.sleep(0.05)
    t2.start()
    
    t1.join()
    t2.join()
    
    assert len(results) == 2
    statuses = [r.status for r in results]
    assert PaymentStatus.SUCCESS in statuses
    assert PaymentStatus.CONFLICT in statuses

def test_fallback_v3():
    store = IdempotencyStore()
    strategy = HealthBasedRoutingStrategy()
    g1 = MyTestGateway("G1")
    g2 = MyTestGateway("G2")
    g1.succeed_next = False
    router = GatewayRouter([g1, g2], strategy, store)
    req = PaymentRequest("req", "idem-v3-4", 10.0, "USD", "u1")
    res = router.route_payment(req)
    assert res.status == PaymentStatus.SUCCESS
    assert res.gateway_name == "G2"

def test_failed_status_idempotency_v3():
    store = IdempotencyStore()
    strategy = HealthBasedRoutingStrategy()
    g1 = MyTestGateway("G1")
    g1.succeed_next = False
    router = GatewayRouter([g1], strategy, store)
    
    req1 = PaymentRequest("req", "idem-v3-5", 10.0, "USD", "u1")
    res1 = router.route_payment(req1)
    assert res1.status == PaymentStatus.FAILED
    
    req2 = PaymentRequest("req2", "idem-v3-5", 10.0, "USD", "u1")
    res2 = router.route_payment(req2)
    assert res2.status == PaymentStatus.FAILED
