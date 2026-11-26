"""Trigger for job-scheduler (v2-extended)."""


class Trigger:
    def __init__(self) -> None:
        self.id = "Trigger"

    def describe(self) -> str:
        return f"Trigger:{self.id}"
