"""LeaseManager for job-scheduler (v3-optimized)."""


class LeaseManager:
    def __init__(self) -> None:
        self.id = "LeaseManager"

    def describe(self) -> str:
        return f"LeaseManager:{self.id}"
