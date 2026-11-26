"""IdempotencyStore for job-scheduler (v3-optimized)."""


class IdempotencyStore:
    def __init__(self) -> None:
        self.id = "IdempotencyStore"

    def describe(self) -> str:
        return f"IdempotencyStore:{self.id}"
