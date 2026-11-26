import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gateway_adapters import StripeGatewayAdapter, RazorpayGatewayAdapter
from router import HealthBasedRoutingStrategy, GatewayRouter
from idempotency_store import IdempotencyStore
from payment_request import PaymentRequest

def main():
    stripe = StripeGatewayAdapter()
    razorpay = RazorpayGatewayAdapter()
    
    strategy = HealthBasedRoutingStrategy()
    store = IdempotencyStore()
    
    router = GatewayRouter([stripe, razorpay], strategy, store)
    
    req1 = PaymentRequest("1", "key123", 100.0, "USD", "user1")
    print("Sending request 1...")
    res1 = router.route_payment(req1)
    print(f"Result: {res1.status} via {res1.gateway_name}")
    
    req2 = PaymentRequest("2", "key123", 100.0, "USD", "user1")
    print("Sending duplicate request 2 with same idempotency key...")
    res2 = router.route_payment(req2)
    print(f"Result: {res2.status} via {res2.gateway_name}")

if __name__ == "__main__":
    main()
