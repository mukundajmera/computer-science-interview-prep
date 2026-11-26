"""
Factory Method Pattern - V3 Advanced (Registry-based Factory)

Uses registration to dynamically add new product types
without modifying the factory class.

Benefits:
- Open/Closed Principle fully satisfied
- New types can be added at runtime
- No if/elif chains
- Very Pythonic using decorators
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, Type, Any

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')



# Product interface
class PaymentProcessor(ABC):
    """Abstract payment processor interface."""
    
    @abstractmethod
    def process_payment(self, amount: float) -> None:
        pass
    
    @abstractmethod
    def refund(self, transaction_id: str, amount: float) -> bool:
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass


# Concrete Products
class CreditCardProcessor(PaymentProcessor):
    """Credit card payment processor."""
    
    def process_payment(self, amount: float) -> None:
        print(f"Processing ${amount:.2f} via Credit Card")
        print("  → Validating card...")
        print("  → Charging card...")
        print("  → Payment successful!")
    
    def refund(self, transaction_id: str, amount: float) -> bool:
        print(f"Refunding ${amount:.2f} to Credit Card (TX: {transaction_id})")
        return True
    
    @property
    def provider_name(self) -> str:
        return "Credit Card"


class PayPalProcessor(PaymentProcessor):
    """PayPal payment processor."""
    
    def process_payment(self, amount: float) -> None:
        print(f"Processing ${amount:.2f} via PayPal")
        print("  → Redirecting to PayPal...")
        print("  → User authenticated...")
        print("  → Payment confirmed!")
    
    def refund(self, transaction_id: str, amount: float) -> bool:
        print(f"Refunding ${amount:.2f} via PayPal (TX: {transaction_id})")
        return True
    
    @property
    def provider_name(self) -> str:
        return "PayPal"


class CryptoProcessor(PaymentProcessor):
    """Cryptocurrency payment processor."""
    
    def __init__(self, currency: str = "BTC"):
        self.currency = currency
    
    def process_payment(self, amount: float) -> None:
        print(f"Processing ${amount:.2f} equivalent in {self.currency}")
        print("  → Generating wallet address...")
        print("  → Waiting for blockchain confirmation...")
        print("  → Payment verified on chain!")
    
    def refund(self, transaction_id: str, amount: float) -> bool:
        print(f"Refunding ${amount:.2f} in {self.currency} (TX: {transaction_id})")
        return True
    
    @property
    def provider_name(self) -> str:
        return f"Crypto ({self.currency})"


# Registry-based Factory
class PaymentProcessorFactory:
    """
    Registry-based factory using class-level registry.
    
    Supports both class registration and callable registration.
    """
    
    _registry: Dict[str, Callable[[], PaymentProcessor]] = {}
    
    @classmethod
    def register(cls, type_name: str, creator: Callable[[], PaymentProcessor] = None):
        """
        Register a payment processor type.
        
        Can be used as a decorator or called directly.
        """
        def decorator(creator_func: Callable[[], PaymentProcessor]):
            cls._registry[type_name.lower()] = creator_func
            print(f"Registered payment processor: {type_name}")
            return creator_func
        
        if creator is not None:
            # Direct call: register(type_name, creator)
            cls._registry[type_name.lower()] = creator
            print(f"Registered payment processor: {type_name}")
            return creator
        
        # Decorator usage: @register(type_name)
        return decorator
    
    @classmethod
    def supports(cls, type_name: str) -> bool:
        """Check if a payment type is supported."""
        return type_name.lower() in cls._registry
    
    @classmethod
    def create(cls, type_name: str) -> PaymentProcessor:
        """Factory method to create a payment processor."""
        creator = cls._registry.get(type_name.lower())
        
        if creator is None:
            raise ValueError(
                f"Unknown payment type: {type_name}. "
                f"Supported types: {list(cls._registry.keys())}"
            )
        
        return creator()
    
    @classmethod
    def list_supported_types(cls) -> None:
        """List all registered payment types."""
        print(f"Supported payment types: {list(cls._registry.keys())}")


# Register built-in types
PaymentProcessorFactory.register("credit_card", CreditCardProcessor)
PaymentProcessorFactory.register("paypal", PayPalProcessor)
PaymentProcessorFactory.register("crypto", CryptoProcessor)
PaymentProcessorFactory.register("bitcoin", lambda: CryptoProcessor("BTC"))
PaymentProcessorFactory.register("ethereum", lambda: CryptoProcessor("ETH"))


# Custom processor that can be registered at runtime
class ApplePayProcessor(PaymentProcessor):
    """Apple Pay payment processor."""
    
    def process_payment(self, amount: float) -> None:
        print(f"Processing ${amount:.2f} via Apple Pay")
        print("  → Authenticating with Face ID...")
        print("  → Payment complete!")
    
    def refund(self, transaction_id: str, amount: float) -> bool:
        print(f"Refunding ${amount:.2f} via Apple Pay (TX: {transaction_id})")
        return True
    
    @property
    def provider_name(self) -> str:
        return "Apple Pay"


# Alternative: Decorator-based registration
def payment_processor(type_name: str):
    """
    Decorator to register a payment processor class.
    
    Usage:
        @payment_processor("stripe")
        class StripeProcessor(PaymentProcessor):
            ...
    """
    def decorator(cls: Type[PaymentProcessor]):
        PaymentProcessorFactory.register(type_name, cls)
        return cls
    return decorator


# Demo
if __name__ == "__main__":
    print("=== Registry-based Factory Demo ===\n")
    
    # List initial registered types
    PaymentProcessorFactory.list_supported_types()
    
    print("\n--- Processing payments with registered types ---\n")
    
    # Use factory to create processors
    card = PaymentProcessorFactory.create("credit_card")
    card.process_payment(99.99)
    
    print()
    
    paypal = PaymentProcessorFactory.create("PayPal")
    paypal.process_payment(49.99)
    
    print()
    
    btc = PaymentProcessorFactory.create("bitcoin")
    btc.process_payment(1000.00)
    
    print("\n--- Registering new payment type at runtime ---\n")
    
    # Register new type at runtime
    PaymentProcessorFactory.register("apple_pay", ApplePayProcessor)
    PaymentProcessorFactory.list_supported_types()
    
    print()
    
    apple = PaymentProcessorFactory.create("apple_pay")
    apple.process_payment(25.00)
    
    print("\n--- Using decorator registration ---\n")
    
    @payment_processor("google_pay")
    class GooglePayProcessor(PaymentProcessor):
        def process_payment(self, amount: float) -> None:
            print(f"Processing ${amount:.2f} via Google Pay")
        
        def refund(self, transaction_id: str, amount: float) -> bool:
            return True
        
        @property
        def provider_name(self) -> str:
            return "Google Pay"
    
    gpay = PaymentProcessorFactory.create("google_pay")
    gpay.process_payment(15.00)
    
    print("\n--- Testing error handling ---\n")
    
    try:
        PaymentProcessorFactory.create("venmo")  # Not registered
    except ValueError as e:
        print(f"Expected error: {e}")
