"""RetryPolicy for payment-system (v2-extended)."""


class RetryPolicy:
    def __init__(self) -> None:
        self.id = "RetryPolicy"

    def describe(self) -> str:
        return f"RetryPolicy:{self.id}"
# Substantive change for review
