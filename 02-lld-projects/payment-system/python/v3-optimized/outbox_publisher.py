"""OutboxPublisher for payment-system (v3-optimized)."""


class OutboxPublisher:
    def __init__(self) -> None:
        self.id = "OutboxPublisher"

    def describe(self) -> str:
        return f"OutboxPublisher:{self.id}"
