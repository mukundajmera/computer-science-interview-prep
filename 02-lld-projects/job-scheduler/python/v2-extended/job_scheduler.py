"""JobScheduler for job-scheduler (v2-extended)."""


class JobScheduler:
    def __init__(self) -> None:
        self.id = "JobScheduler"

    def describe(self) -> str:
        return f"JobScheduler:{self.id}"
