"""PaymentGateway for payment-system (v1-basic)."""


class PaymentGateway:
    def __init__(self) -> None:
        self.id = "PaymentGateway"

    def describe(self) -> str:
        return f"PaymentGateway:{self.id}"
