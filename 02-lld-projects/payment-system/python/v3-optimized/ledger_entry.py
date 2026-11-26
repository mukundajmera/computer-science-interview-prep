"""LedgerEntry for payment-system (v3-optimized)."""


class LedgerEntry:
    def __init__(self) -> None:
        self.id = "LedgerEntry"

    def describe(self) -> str:
        return f"LedgerEntry:{self.id}"
