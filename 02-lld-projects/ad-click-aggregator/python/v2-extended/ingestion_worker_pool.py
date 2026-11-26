"""IngestionWorkerPool for ad-click-aggregator (v2-extended)."""

class IngestionWorkerPool:
    def __init__(self, num_workers: int = 4) -> None:
        self.num_workers = num_workers
