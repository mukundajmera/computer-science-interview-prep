"""
Adapter Pattern - V2 Pythonic: Payment Gateway Adapter

Real-world scenario using Python idioms like duck typing,
dataclasses, and protocol classes.
"""
from dataclasses import dataclass
from typing import Dict, Any, Protocol


# Protocol-based Target (Python 3.8+)
class PaymentProcessor(Protocol):
    """Protocol for payment processors - duck typing alternative to ABC"""
    def process_payment(self, amount: float, currency: str, 
                       card_details: Dict[str, str]) -> bool: ...
    def refund(self, transaction_id: str, amount: float) -> bool: ...
    def get_provider_name(self) -> str: ...


# Adaptee 1 - Stripe-like API
@dataclass
class StripeCharge:
    charge_id: str
    amount_cents: int
    currency: str


class StripeAPI:
    def create_charge(self, amount_cents: int, currency: str, 
                     card_token: str) -> StripeCharge:
        print(f"Stripe: Charging {amount_cents} cents in {currency}")
        import time
        return StripeCharge(
            charge_id=f"stripe_txn_{int(time.time())}",
            amount_cents=amount_cents,
            currency=currency
        )
    
    def create_refund(self, charge_id: str, amount_cents: int) -> bool:
        print(f"Stripe: Refunding {amount_cents} cents for {charge_id}")
        return True
    
    def create_card_token(self, card_number: str, expiry: str, cvv: str) -> str:
        return f"tok_{card_number[-4:]}"


# Adaptee 2 - PayPal-like API
@dataclass
class PayPalPayment:
    amount: float
    currency: str
    transaction_id: str = None
    status: str = "PENDING"


class PayPalSDK:
    def create_payment(self, amount: float, currency_code: str) -> PayPalPayment:
        return PayPalPayment(amount=amount, currency=currency_code)
    
    def execute_payment(self, payment: PayPalPayment, payer_id: str) -> PayPalPayment:
        print(f"PayPal: Executing payment of {payment.amount} {payment.currency}")
        import time
        payment.transaction_id = f"pp_{int(time.time())}"
        payment.status = "COMPLETED"
        return payment
    
    def refund_payment(self, transaction_id: str, amount: float) -> bool:
        print(f"PayPal: Refunding {amount} for {transaction_id}")
        return True


# Adapter for Stripe
class StripeAdapter:
    """Adapts Stripe API to PaymentProcessor protocol"""
    
    def __init__(self, stripe: StripeAPI):
        self._stripe = stripe
        self._last_charge: StripeCharge = None
    
    def process_payment(self, amount: float, currency: str,
                       card_details: Dict[str, str]) -> bool:
        # Convert dollars to cents
        amount_cents = int(amount * 100)
        
        # Create token from card details
        token = self._stripe.create_card_token(
            card_details.get("number", ""),
            card_details.get("expiry", ""),
            card_details.get("cvv", "")
        )
        
        # Process payment
        self._last_charge = self._stripe.create_charge(amount_cents, currency, token)
        return self._last_charge is not None
    
    def refund(self, transaction_id: str, amount: float) -> bool:
        return self._stripe.create_refund(transaction_id, int(amount * 100))
    
    def get_provider_name(self) -> str:
        return "Stripe"


# Adapter for PayPal
class PayPalAdapter:
    """Adapts PayPal SDK to PaymentProcessor protocol"""
    
    def __init__(self, paypal: PayPalSDK):
        self._paypal = paypal
    
    def process_payment(self, amount: float, currency: str,
                       card_details: Dict[str, str]) -> bool:
        payment = self._paypal.create_payment(amount, currency)
        result = self._paypal.execute_payment(payment, "PAYER_ID")
        return result.status == "COMPLETED"
    
    def refund(self, transaction_id: str, amount: float) -> bool:
        return self._paypal.refund_payment(transaction_id, amount)
    
    def get_provider_name(self) -> str:
        return "PayPal"


# Pythonic function-based adapter using closures
def create_payment_adapter(api: Any, adapter_type: str) -> PaymentProcessor:
    """Factory function that creates adapters dynamically"""
    
    if adapter_type == "stripe":
        return StripeAdapter(api)
    elif adapter_type == "paypal":
        return PayPalAdapter(api)
    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")


# Client code using duck typing
class PaymentService:
    def __init__(self):
        self._processor: PaymentProcessor = None
    
    def set_processor(self, processor: PaymentProcessor) -> None:
        self._processor = processor
        print(f"Using payment provider: {processor.get_provider_name()}")
    
    def checkout(self, amount: float, card: Dict[str, str]) -> bool:
        return self._processor.process_payment(amount, "USD", card)


# Demo
if __name__ == "__main__":
    service = PaymentService()
    card = {
        "number": "4111111111111111",
        "expiry": "12/25",
        "cvv": "123"
    }
    
    # Use Stripe via factory
    stripe_adapter = create_payment_adapter(StripeAPI(), "stripe")
    service.set_processor(stripe_adapter)
    service.checkout(99.99, card)
    
    print()
    
    # Use PayPal via factory
    paypal_adapter = create_payment_adapter(PayPalSDK(), "paypal")
    service.set_processor(paypal_adapter)
    service.checkout(49.99, card)
