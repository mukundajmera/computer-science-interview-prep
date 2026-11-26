"""DeadLetterQueue for job-scheduler (v3-optimized)."""


class DeadLetterQueue:
    def __init__(self) -> None:
        self.id = "DeadLetterQueue"

    def describe(self) -> str:
        return f"DeadLetterQueue:{self.id}"
