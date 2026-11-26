"""PaymentMethod for payment-system (v1-basic)."""


class PaymentMethod:
    def __init__(self) -> None:
        self.id = "PaymentMethod"

    def describe(self) -> str:
        return f"PaymentMethod:{self.id}"
