"""Money for payment-system (v1-basic)."""


class Money:
    def __init__(self) -> None:
        self.id = "Money"

    def describe(self) -> str:
        return f"Money:{self.id}"
