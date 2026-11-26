"""
Facade Pattern - V2 Variant: E-commerce Checkout.

The facade hides inventory, payment, shipping, and notification calls behind
one interview-friendly checkout operation.
"""
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class OrderConfirmation:
    order_id: str
    payment_id: str
    shipment_id: str
    total: float


class InventoryService:
    """Subsystem for stock checks and reservations."""

    def __init__(self, stock_by_item: Dict[str, int]):
        self._stock_by_item = dict(stock_by_item)

    def available(self, item_id: str) -> int:
        return self._stock_by_item.get(item_id, 0)

    def reserve(self, item_id: str, quantity: int) -> None:
        if self.available(item_id) < quantity:
            raise ValueError(f"Insufficient stock for {item_id}")
        self._stock_by_item[item_id] -= quantity


class PaymentService:
    """Subsystem for payment authorization."""

    def charge(self, amount: float, card_token: str) -> str:
        if not card_token:
            raise ValueError("card_token is required")
        return f"pay-{int(round(amount * 100))}"


class ShippingService:
    """Subsystem for shipping quotes and labels."""

    SHIPPING_FEE = 5.00

    def quote(self, address: str) -> float:
        if not address:
            raise ValueError("address is required")
        return self.SHIPPING_FEE

    def create_shipment(self, item_id: str, quantity: int, address: str) -> str:
        if not address:
            raise ValueError("address is required")
        return f"ship-{item_id}-{quantity}"


class NotificationService:
    """Subsystem for customer notifications."""

    def send_confirmation(self, email: str, order_id: str) -> str:
        if "@" not in email:
            raise ValueError("valid email is required")
        return f"sent:{email}:{order_id}"


class CheckoutFacade:
    """Simplified API for placing an order."""

    def __init__(
        self,
        inventory: InventoryService,
        payment: PaymentService,
        shipping: ShippingService,
        notifications: NotificationService,
    ):
        self._inventory = inventory
        self._payment = payment
        self._shipping = shipping
        self._notifications = notifications

    def place_order(
        self,
        item_id: str,
        quantity: int,
        unit_price: float,
        card_token: str,
        address: str,
        email: str,
    ) -> OrderConfirmation:
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        self._inventory.reserve(item_id, quantity)
        total = unit_price * quantity + self._shipping.quote(address)
        payment_id = self._payment.charge(total, card_token)
        shipment_id = self._shipping.create_shipment(item_id, quantity, address)
        order_id = f"order-{item_id}-{quantity}"
        self._notifications.send_confirmation(email, order_id)
        return OrderConfirmation(order_id, payment_id, shipment_id, total)


if __name__ == "__main__":
    checkout = CheckoutFacade(
        InventoryService({"book": 3}),
        PaymentService(),
        ShippingService(),
        NotificationService(),
    )
    print(
        checkout.place_order(
            "book",
            1,
            20.00,
            "tok_123",
            "10 Main St",
            "reader@example.com",
        )
    )
