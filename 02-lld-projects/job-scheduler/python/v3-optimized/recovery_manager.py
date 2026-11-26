"""RecoveryManager for job-scheduler (v3-optimized)."""


class RecoveryManager:
    def __init__(self) -> None:
        self.id = "RecoveryManager"

    def describe(self) -> str:
        return f"RecoveryManager:{self.id}"
