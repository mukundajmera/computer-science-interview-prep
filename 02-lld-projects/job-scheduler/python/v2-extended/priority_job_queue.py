"""PriorityJobQueue for job-scheduler (v2-extended)."""


class PriorityJobQueue:
    def __init__(self) -> None:
        self.id = "PriorityJobQueue"

    def describe(self) -> str:
        return f"PriorityJobQueue:{self.id}"
