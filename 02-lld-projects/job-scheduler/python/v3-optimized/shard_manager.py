"""ShardManager for job-scheduler (v3-optimized)."""


class ShardManager:
    def __init__(self) -> None:
        self.id = "ShardManager"

    def describe(self) -> str:
        return f"ShardManager:{self.id}"
