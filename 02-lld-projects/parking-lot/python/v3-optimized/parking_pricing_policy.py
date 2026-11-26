"""Interview-oriented policy contracts for parking lot pricing and assignment."""

from __future__ import annotations

from typing import Protocol


class ParkingPricingPolicy(Protocol):
    """Contract for computing parking fee from a ticket record."""

    def calculate_fee(self, ticket: object) -> float:
        ...


class TicketLifecycleHook(Protocol):
    """Hook points around ticket lifecycle events."""

    def on_ticket_opened(self, ticket: object) -> None:
        ...

    def on_ticket_closed(self, ticket: object, final_fee: float) -> None:
        ...


class VehicleFitPolicy(Protocol):
    """Policy contract for spot assignment checks."""

    def can_assign(self, vehicle: object, spot: object) -> bool:
        ...
