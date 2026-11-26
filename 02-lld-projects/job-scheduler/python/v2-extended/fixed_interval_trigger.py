"""FixedIntervalTrigger for job-scheduler (v2-extended)."""


class FixedIntervalTrigger:
    def __init__(self) -> None:
        self.id = "FixedIntervalTrigger"

    def describe(self) -> str:
        return f"FixedIntervalTrigger:{self.id}"
