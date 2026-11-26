import time
from typing import List, Dict, Optional

class Replica:
    def __init__(self, replica_id: str):
        self.id = replica_id
        self.healthy: bool = True
        self.lag_ms: int = 0

class ReadReplicaRouter:
    def __init__(self, primary: str, replica_ids: List[str], max_lag_ms: int):
        self.primary = primary
        self.replicas = [Replica(rid) for rid in replica_ids]
        self.max_lag_ms = max_lag_ms
        self.user_last_write: Dict[str, int] = {}
        self.rr_index = 0
        self.mock_time_ms: Optional[int] = None

    def _now(self) -> int:
        if self.mock_time_ms is not None:
            return self.mock_time_ms
        return int(time.time() * 1000)

    def set_mock_time(self, mock_time_ms: int) -> None:
        self.mock_time_ms = mock_time_ms

    def route_write(self, user_id: str) -> str:
        self.user_last_write[user_id] = self._now()
        return self.primary

    def route_read(self, user_id: str) -> str:
        now = self._now()
        last_write = self.user_last_write.get(user_id)

        eligible: List[Replica] = []
        for r in self.replicas:
            if not r.healthy:
                continue
            if r.lag_ms > self.max_lag_ms:
                continue

            # Read-your-own-writes check
            if last_write is not None:
                elapsed = now - last_write
                if r.lag_ms >= elapsed:
                    continue

            eligible.append(r)

        if not eligible:
            return self.primary

        selected = eligible[self.rr_index % len(eligible)].id
        self.rr_index += 1
        return selected

    def update_replica_health(self, replica_id: str, healthy: bool) -> None:
        for r in self.replicas:
            if r.id == replica_id:
                r.healthy = healthy
                break

    def update_replica_lag(self, replica_id: str, lag_ms: int) -> None:
        for r in self.replicas:
            if r.id == replica_id:
                r.lag_ms = lag_ms
                break
