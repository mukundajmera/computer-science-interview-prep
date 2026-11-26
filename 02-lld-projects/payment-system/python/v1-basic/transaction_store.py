"""TransactionStore for payment-system (v1-basic)."""


class TransactionStore:
    def __init__(self) -> None:
        self.id = "TransactionStore"

    def describe(self) -> str:
        return f"TransactionStore:{self.id}"
