"""Interview-focused workflow contracts for vending-machine dispensing."""

from __future__ import annotations

from typing import Protocol


class MachineStateTransition(Protocol):
    """Handles machine state movement in workflow."""

    def move(self, machine: object, next_state: str) -> None:
        ...


class PaymentCommand(Protocol):
    """Applies payment-side effects before dispense."""

    def apply(self, machine: object) -> None:
        ...


class InventoryReservationPolicy(Protocol):
    """Reserves inventory atomically for selected slot."""

    def try_reserve(self, slot: object) -> bool:
        ...


class DispenseWorkflowPolicy:
    """Composes transition, payment, and reservation contracts."""

    def __init__(
        self,
        state_transition: MachineStateTransition,
        payment_command: PaymentCommand,
        inventory_reservation_policy: InventoryReservationPolicy,
    ) -> None:
        self._state_transition = state_transition
        self._payment_command = payment_command
        self._inventory_reservation_policy = inventory_reservation_policy

    def execute(self, machine: object, slot: object) -> bool:
        if not self._inventory_reservation_policy.try_reserve(slot):
            return False
        self._payment_command.apply(machine)
        self._state_transition.move(machine, "DISPENSING")
        return True
