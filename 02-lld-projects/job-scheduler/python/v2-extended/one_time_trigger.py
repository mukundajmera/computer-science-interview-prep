"""OneTimeTrigger for job-scheduler (v2-extended)."""


class OneTimeTrigger:
    def __init__(self) -> None:
        self.id = "OneTimeTrigger"

    def describe(self) -> str:
        return f"OneTimeTrigger:{self.id}"
