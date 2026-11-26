from dataclasses import dataclass
from typing import List, Protocol


@dataclass(frozen=True)
class LeaderboardEntry:
    actor_id: str
    score: float
    updated_at_ms: int


@dataclass(frozen=True)
class LeaderboardSnapshot:
    leaderboard_id: str
    entries: List[LeaderboardEntry]
    computed_at_ms: int


class LeaderboardProjection(Protocol):
    """Projection contract for ranking materialization."""

    def record_result(
        self, leaderboard_id: str, actor_id: str, score: float, event_timestamp_ms: int
    ) -> None: ...

    def top_k(self, leaderboard_id: str, k: int) -> List[LeaderboardEntry]: ...

    def snapshot(self, leaderboard_id: str, limit: int) -> LeaderboardSnapshot: ...


class MetricsLeaderboardService(Protocol):
    """Service boundary for metrics-to-leaderboard flow."""

    def ingest_point(
        self, metric_name: str, actor_id: str, value: float, timestamp_ms: int
    ) -> None: ...

    def get_snapshot(self, leaderboard_id: str, limit: int) -> LeaderboardSnapshot: ...
