"""
Strategy Pattern - V1 Basic: Payment Processing
"""
from abc import ABC, abstractmethod
from typing import Optional


# Strategy Interface
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> None:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass


# Concrete Strategies
class CreditCardPayment(PaymentStrategy):
    def __init__(self, card_number: str, name: str):
        self.card_number = card_number
        self.name = name
    
    def pay(self, amount: float) -> None:
        print(f"Paid ${amount:.2f} with Credit Card ending in {self.card_number[-4:]}")
    
    def get_name(self) -> str:
        return "Credit Card"


class PayPalPayment(PaymentStrategy):
    def __init__(self, email: str):
        self.email = email
    
    def pay(self, amount: float) -> None:
        print(f"Paid ${amount:.2f} via PayPal account: {self.email}")
    
    def get_name(self) -> str:
        return "PayPal"


class CryptoPayment(PaymentStrategy):
    def __init__(self, wallet_address: str):
        self.wallet_address = wallet_address
    
    def pay(self, amount: float) -> None:
        print(f"Paid ${amount:.2f} in crypto to wallet: {self.wallet_address[:8]}...")
    
    def get_name(self) -> str:
        return "Cryptocurrency"


# Context
class ShoppingCart:
    def __init__(self):
        self._items: list = []
        self._total: float = 0.0
        self._payment_strategy: Optional[PaymentStrategy] = None
    
    def add_item(self, item: str, price: float) -> None:
        self._items.append((item, price))
        self._total += price
        print(f"Added: {item} - ${price:.2f}")
    
    def set_payment_strategy(self, strategy: PaymentStrategy) -> None:
        self._payment_strategy = strategy
        print(f"Payment method: {strategy.get_name()}")
    
    def checkout(self) -> None:
        if self._payment_strategy is None:
            raise RuntimeError("No payment method selected")
        
        print("\n--- Checkout ---")
        print(f"Total: ${self._total:.2f}")
        self._payment_strategy.pay(self._total)
        self._items.clear()
        self._total = 0.0


if __name__ == "__main__":
    cart = ShoppingCart()
    
    # Add items
    cart.add_item("Laptop", 999.99)
    cart.add_item("Mouse", 29.99)
    
    # Pay with Credit Card
    cart.set_payment_strategy(CreditCardPayment("4111111111111111", "John Doe"))
    cart.checkout()
    
    # Different order with PayPal
    print("\n=== New Order ===")
    cart.add_item("Keyboard", 149.99)
    cart.set_payment_strategy(PayPalPayment("john@example.com"))
    cart.checkout()
    
    # Another order with Crypto
    print("\n=== New Order ===")
    cart.add_item("Monitor", 299.99)
    cart.set_payment_strategy(CryptoPayment("0x742d35Cc6634C0532925a3b844Bc454e4438f44e"))
    cart.checkout()
