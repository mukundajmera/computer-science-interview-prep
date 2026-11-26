"""PaymentService for payment-system (v2-extended)."""


class PaymentService:
    def __init__(self) -> None:
        self.id = "PaymentService"

    def describe(self) -> str:
        return f"PaymentService:{self.id}"
# Substantive change for review
