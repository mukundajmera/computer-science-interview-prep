"""DisputeManager for payment-system (v3-optimized)."""


class DisputeManager:
    def __init__(self) -> None:
        self.id = "DisputeManager"

    def describe(self) -> str:
        return f"DisputeManager:{self.id}"
