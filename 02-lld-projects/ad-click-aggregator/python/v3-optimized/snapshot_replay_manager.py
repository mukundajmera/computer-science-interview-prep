"""SnapshotReplayManager for ad-click-aggregator (v3-optimized)."""

class SnapshotReplayManager:
    def __init__(self) -> None:
        self.snapshot_version = 0

    def take_snapshot(self) -> None:
        self.snapshot_version += 1
