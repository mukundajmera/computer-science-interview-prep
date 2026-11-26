"""ExponentialBackoffPolicy for job-scheduler (v2-extended)."""


class ExponentialBackoffPolicy:
    def __init__(self) -> None:
        self.id = "ExponentialBackoffPolicy"

    def describe(self) -> str:
        return f"ExponentialBackoffPolicy:{self.id}"
