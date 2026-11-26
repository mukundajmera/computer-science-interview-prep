"""PaymentService for payment-system (v1-basic)."""


class PaymentService:
    def __init__(self) -> None:
        self.id = "PaymentService"

    def describe(self) -> str:
        return f"PaymentService:{self.id}"
# v1-basic intent core baseline
