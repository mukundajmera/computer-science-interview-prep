"""PaymentRequest for payment-system (v1-basic)."""


class PaymentRequest:
    def __init__(self) -> None:
        self.id = "PaymentRequest"

    def describe(self) -> str:
        return f"PaymentRequest:{self.id}"
