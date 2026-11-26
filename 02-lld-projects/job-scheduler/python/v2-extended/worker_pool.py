"""WorkerPool for job-scheduler (v2-extended)."""


class WorkerPool:
    def __init__(self) -> None:
        self.id = "WorkerPool"

    def describe(self) -> str:
        return f"WorkerPool:{self.id}"
