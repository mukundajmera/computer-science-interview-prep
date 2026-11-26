"""SchedulerMetrics for job-scheduler (v2-extended)."""


class SchedulerMetrics:
    def __init__(self) -> None:
        self.id = "SchedulerMetrics"

    def describe(self) -> str:
        return f"SchedulerMetrics:{self.id}"
