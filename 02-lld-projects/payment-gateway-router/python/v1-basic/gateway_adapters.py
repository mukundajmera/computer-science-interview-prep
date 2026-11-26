from abc import ABC, abstractmethod
from typing import List, Deque
from collections import deque
import uuid
import threading
from payment_request import PaymentRequest
from payment_response import PaymentResponse, PaymentStatus
from circuit_breaker import CircuitBreaker

class PaymentGateway(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        pass

    @abstractmethod
    def get_success_rate(self) -> float:
        pass

    @abstractmethod
    def record_metrics(self, success: bool):
        pass

class AbstractPaymentGateway(PaymentGateway):
    def __init__(self, name: str):
        self.name = name
        self.window: Deque[bool] = deque(maxlen=10)
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, reset_timeout_ms=5000)
        self.lock = threading.Lock()

    def get_name(self) -> str:
        return self.name

    def record_metrics(self, success: bool):
        with self.lock:
            self.window.append(success)
            if success:
                self.circuit_breaker.record_success()
            else:
                self.circuit_breaker.record_failure()

    def get_success_rate(self) -> float:
        with self.lock:
            if not self.window:
                return 1.0
            successes = sum(1 for x in self.window if x)
            return successes / len(self.window)

class StripeGatewayAdapter(AbstractPaymentGateway):
    def __init__(self):
        super().__init__("Stripe")

    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        if not self.circuit_breaker.allow_request():
            return PaymentResponse(None, PaymentStatus.FAILED, "Circuit breaker open", self.name)

        success = self.simulate_network_call()
        
        if success:
            self.record_metrics(True)
            return PaymentResponse(str(uuid.uuid4()), PaymentStatus.SUCCESS, "Payment processed by Stripe", self.name)
        else:
            self.record_metrics(False)
            return PaymentResponse(None, PaymentStatus.TIMEOUT, "Stripe timeout", self.name)

    def simulate_network_call(self) -> bool:
        return True

class RazorpayGatewayAdapter(AbstractPaymentGateway):
    def __init__(self):
        super().__init__("Razorpay")

    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        if not self.circuit_breaker.allow_request():
            return PaymentResponse(None, PaymentStatus.FAILED, "Circuit breaker open", self.name)

        success = self.simulate_network_call()
        
        if success:
            self.record_metrics(True)
            return PaymentResponse(str(uuid.uuid4()), PaymentStatus.SUCCESS, "Payment processed by Razorpay", self.name)
        else:
            self.record_metrics(False)
            return PaymentResponse(None, PaymentStatus.TIMEOUT, "Razorpay timeout", self.name)

    def simulate_network_call(self) -> bool:
        return True
