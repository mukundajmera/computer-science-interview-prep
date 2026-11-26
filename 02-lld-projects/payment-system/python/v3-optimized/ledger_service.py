"""LedgerService for payment-system (v3-optimized)."""


class LedgerService:
    def __init__(self) -> None:
        self.id = "LedgerService"

    def describe(self) -> str:
        return f"LedgerService:{self.id}"
