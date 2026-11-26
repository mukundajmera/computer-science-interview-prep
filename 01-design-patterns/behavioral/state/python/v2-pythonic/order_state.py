"""
State Pattern - V2 Pythonic: Order Lifecycle

Models an e-commerce order as a finite state machine. Each state owns the
operations that are legal from that point in the lifecycle.
"""
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Optional


class OrderState(ABC):
    """Base state with default guards for unsupported transitions."""

    status = "UNKNOWN"

    def pay(self, order: "Order", method: str) -> None:
        raise ValueError(f"Cannot pay while order is {order.status}")

    def ship(self, order: "Order", tracking_number: str) -> None:
        raise ValueError(f"Cannot ship while order is {order.status}")

    def deliver(self, order: "Order") -> None:
        raise ValueError(f"Cannot deliver while order is {order.status}")

    def cancel(self, order: "Order", reason: str) -> None:
        raise ValueError(f"Cannot cancel while order is {order.status}")


class PendingState(OrderState):
    status = "PENDING"

    def pay(self, order: "Order", method: str) -> None:
        order.payment_method = method
        order.set_state(PaidState())

    def cancel(self, order: "Order", reason: str) -> None:
        order.cancel_reason = reason
        order.set_state(CancelledState())


class PaidState(OrderState):
    status = "PAID"

    def ship(self, order: "Order", tracking_number: str) -> None:
        order.tracking_number = tracking_number
        order.set_state(ShippedState())

    def cancel(self, order: "Order", reason: str) -> None:
        order.cancel_reason = reason
        order.set_state(CancelledState())


class ShippedState(OrderState):
    status = "SHIPPED"

    def deliver(self, order: "Order") -> None:
        order.set_state(DeliveredState())

    def cancel(self, order: "Order", reason: str) -> None:
        raise ValueError("Cannot cancel after shipment has started")


class DeliveredState(OrderState):
    status = "DELIVERED"


class CancelledState(OrderState):
    status = "CANCELLED"


@dataclass
class Order:
    """Context that delegates lifecycle operations to the current state."""

    order_id: str
    state: OrderState = field(default_factory=PendingState)
    payment_method: Optional[str] = None
    tracking_number: Optional[str] = None
    cancel_reason: Optional[str] = None
    history: List[str] = field(default_factory=lambda: ["CREATED"])

    @property
    def status(self) -> str:
        return self.state.status

    def set_state(self, state: OrderState) -> None:
        self.state = state
        self.history.append(state.status)

    def pay(self, method: str) -> None:
        self.state.pay(self, method)

    def ship(self, tracking_number: str) -> None:
        self.state.ship(self, tracking_number)

    def deliver(self) -> None:
        self.state.deliver(self)

    def cancel(self, reason: str) -> None:
        self.state.cancel(self, reason)


if __name__ == "__main__":
    order = Order("order-1001")
    order.pay("card")
    order.ship("TRK-1")
    order.deliver()
    print(f"{order.order_id}: {order.status}")
    print(" -> ".join(order.history))
