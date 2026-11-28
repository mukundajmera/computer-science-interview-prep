"""
v2-extended real-time gaming leaderboard.

Improvements over v1-basic (each has dedicated tests):

1. Cheat-resistant score validation (FOLLOW-UPS.md #3): increments above
   a configured per-update cap are rejected as anomalous instead of
   entering the ranking, rejections are counted, and rejected updates
   never reach the event log. This models the server-side validation the
   doc demands in place of trusting raw client scores.

2. Durable event log with replay rebuild (FOLLOW-UPS.md #4, PITFALLS.md
   #2): every accepted update is appended to an event log, and
   replay_log() rebuilds the full ranking state from it - the in-memory
   version of reconciling a fresh Redis primary against the MySQL source
   of truth after a failover.

3. Hot-shard hash subdivision (FOLLOW-UPS.md #5): the densest score
   bucket (the one every new player starts in) is subdivided into N hash
   sub-shards by user id, spreading write contention the way
   bucket_0_100_shard_1..N would. Top-k, rank and relative window
   scatter-gather across sub-shards so global ordering is preserved.
"""

import bisect
import threading
import zlib
from typing import Dict, List, Optional, Tuple


class LeaderboardEntry:
    def __init__(self, user_id: str, score: int, timestamp: int):
        self.user_id = user_id
        self.score = score
        self.timestamp = timestamp

    def __lt__(self, other):
        # Higher score comes first
        if self.score != other.score:
            return self.score > other.score
        # Tie-breaker: earlier timestamp comes first
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        return self.user_id < other.user_id

    def __eq__(self, other):
        if not isinstance(other, LeaderboardEntry):
            return False
        return (self.score == other.score and
                self.timestamp == other.timestamp and
                self.user_id == other.user_id)

    def __hash__(self):
        return hash((self.user_id, self.score, self.timestamp))


class PartitionLeaderboard:
    def __init__(self):
        self.sorted_entries: List[LeaderboardEntry] = []
        self.user_map: Dict[str, LeaderboardEntry] = {}
        self.lock = threading.RLock()

    def update_score(self, user_id: str, new_score: int, timestamp: int):
        with self.lock:
            old_entry = self.user_map.get(user_id)
            if old_entry:
                idx = bisect.bisect_left(self.sorted_entries, old_entry)
                if idx < len(self.sorted_entries) and self.sorted_entries[idx] == old_entry:
                    self.sorted_entries.pop(idx)

            new_entry = LeaderboardEntry(user_id, new_score, timestamp)
            bisect.insort(self.sorted_entries, new_entry)
            self.user_map[user_id] = new_entry

    def remove_user(self, user_id: str):
        with self.lock:
            old_entry = self.user_map.pop(user_id, None)
            if old_entry:
                idx = bisect.bisect_left(self.sorted_entries, old_entry)
                if idx < len(self.sorted_entries) and self.sorted_entries[idx] == old_entry:
                    self.sorted_entries.pop(idx)

    def get_rank(self, user_id: str) -> int:
        with self.lock:
            entry = self.user_map.get(user_id)
            if not entry:
                return -1
            idx = bisect.bisect_left(self.sorted_entries, entry)
            if idx < len(self.sorted_entries) and self.sorted_entries[idx] == entry:
                return idx + 1
            return -1

    def __len__(self):
        return len(self.sorted_entries)


class LeaderboardService:
    def __init__(self, partition_size: int = 1000,
                 max_increment: Optional[int] = None,
                 dense_subdivisions: int = 1):
        self.partition_size = partition_size
        # Improvement #1: per-update anomaly cap (None disables, v1 behavior).
        self.max_increment = max_increment
        self.suspicious_rejected = 0
        # Improvement #3: hash sub-shards for the densest (lowest) bucket.
        if dense_subdivisions < 1:
            raise ValueError("dense_subdivisions must be >= 1")
        self.dense_subdivisions = dense_subdivisions
        # bound -> list of sub-partitions (length 1 unless subdivided)
        self.partitions: Dict[int, List[PartitionLeaderboard]] = {}
        self.user_scores: Dict[str, int] = {}
        # Improvement #2: durable event log of accepted updates.
        self.event_log: List[Tuple[str, int, int]] = []
        self.lock = threading.RLock()

    # -- improvement #3 helpers -------------------------------------------

    def _subdivisions_for(self, bound: int) -> int:
        # Only the densest lowest bucket is subdivided (FOLLOW-UPS.md #5).
        return self.dense_subdivisions if bound == 0 else 1

    def _sub_index(self, user_id: str, count: int) -> int:
        return zlib.crc32(user_id.encode("utf-8")) % count

    def _get_partition_lists(self, bound: int) -> List[PartitionLeaderboard]:
        if bound not in self.partitions:
            self.partitions[bound] = [PartitionLeaderboard() for _ in range(self._subdivisions_for(bound))]
        return self.partitions[bound]

    def _route(self, bound: int, user_id: str) -> PartitionLeaderboard:
        subs = self._get_partition_lists(bound)
        return subs[self._sub_index(user_id, len(subs))]

    @staticmethod
    def _merged_entries(subs: List[PartitionLeaderboard]) -> List[LeaderboardEntry]:
        merged: List[LeaderboardEntry] = []
        for sub in subs:
            with sub.lock:
                merged.extend(sub.sorted_entries)
        merged.sort()
        return merged

    def _partition_size(self, bound: int) -> int:
        return sum(len(sub) for sub in self.partitions.get(bound, []))

    # -- core API (v1-compatible signatures) --------------------------------

    def increment_score(self, user_id: str, score_increment: int, timestamp: int) -> bool:
        """Increment a player's score. Returns True when accepted.

        Improvement #1: increments above max_increment are rejected as
        anomalous and counted; nothing is stored or logged for them.
        """
        with self.lock:
            if self.max_increment is not None and score_increment > self.max_increment:
                self.suspicious_rejected += 1
                return False

            current_score = self.user_scores.get(user_id, 0)
            new_score = current_score + score_increment

            old_bound = (current_score // self.partition_size) * self.partition_size
            new_bound = (new_score // self.partition_size) * self.partition_size

            if user_id in self.user_scores and old_bound != new_bound:
                if old_bound in self.partitions:
                    self._route(old_bound, user_id).remove_user(user_id)

            self.user_scores[user_id] = new_score
            self._route(new_bound, user_id).update_score(user_id, new_score, timestamp)
            # Improvement #2: only accepted updates reach the durable log.
            self.event_log.append((user_id, score_increment, timestamp))
            return True

    def get_top_k(self, k: int) -> List[LeaderboardEntry]:
        with self.lock:
            result = []
            for bound in sorted(self.partitions.keys(), reverse=True):
                remaining = k - len(result)
                if remaining <= 0:
                    break
                result.extend(self._merged_entries(self.partitions[bound])[:remaining])
            return result

    def get_rank(self, user_id: str) -> int:
        with self.lock:
            score = self.user_scores.get(user_id)
            if score is None:
                return -1

            target_bound = (score // self.partition_size) * self.partition_size
            global_rank = 1

            for bound in sorted(self.partitions.keys(), reverse=True):
                if bound > target_bound:
                    global_rank += self._partition_size(bound)
                elif bound == target_bound:
                    # Scatter-gather: rank inside the merged bucket.
                    entry = None
                    merged = self._merged_entries(self.partitions[bound])
                    for idx, e in enumerate(merged):
                        if e.user_id == user_id:
                            entry = idx + 1
                            break
                    if entry is not None:
                        return global_rank + entry - 1
                else:
                    break
            return -1

    def get_relative_window(self, user_id: str, radius: int) -> List[LeaderboardEntry]:
        with self.lock:
            rank = self.get_rank(user_id)
            if rank == -1:
                return []

            min_rank = max(1, rank - radius)
            max_rank = rank + radius

            window = []
            current_rank = 1
            for bound in sorted(self.partitions.keys(), reverse=True):
                for entry in self._merged_entries(self.partitions[bound]):
                    if min_rank <= current_rank <= max_rank:
                        window.append(entry)
                    if current_rank > max_rank:
                        return window
                    current_rank += 1
            return window

    def get_score(self, user_id: str) -> Optional[int]:
        with self.lock:
            return self.user_scores.get(user_id)

    # -- improvement #2: replay rebuild --------------------------------------

    def replay_log(self, event_log: List[Tuple[str, int, int]]):
        """Rebuild the full ranking state from a durable event log.

        This is the reconciliation answer to a crashed in-memory primary
        (FOLLOW-UPS.md #4): wipe, then replay every accepted update in
        order. Validation is bypassed because the log only ever holds
        updates that were already accepted.
        """
        with self.lock:
            self.partitions = {}
            self.user_scores = {}
            self.event_log = []
            for user_id, score_increment, timestamp in event_log:
                current_score = self.user_scores.get(user_id, 0)
                new_score = current_score + score_increment

                old_bound = (current_score // self.partition_size) * self.partition_size
                new_bound = (new_score // self.partition_size) * self.partition_size

                if user_id in self.user_scores and old_bound != new_bound:
                    if old_bound in self.partitions:
                        self._route(old_bound, user_id).remove_user(user_id)

                self.user_scores[user_id] = new_score
                self._route(new_bound, user_id).update_score(user_id, new_score, timestamp)
                self.event_log.append((user_id, score_increment, timestamp))
