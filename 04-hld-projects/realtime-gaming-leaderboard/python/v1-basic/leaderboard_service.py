import bisect
import threading
from typing import Dict, List, Tuple, Optional


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
                # bisect doesn't have a direct remove, but we can find and pop
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
    def __init__(self, partition_size: int = 1000):
        self.partition_size = partition_size
        self.partitions: Dict[int, PartitionLeaderboard] = {}
        self.user_scores: Dict[str, int] = {}
        self.lock = threading.RLock()

    def _get_partition(self, score: int) -> PartitionLeaderboard:
        lower_bound = (score // self.partition_size) * self.partition_size
        if lower_bound not in self.partitions:
            self.partitions[lower_bound] = PartitionLeaderboard()
        return self.partitions[lower_bound]

    def increment_score(self, user_id: str, score_increment: int, timestamp: int):
        with self.lock:
            current_score = self.user_scores.get(user_id, 0)
            new_score = current_score + score_increment

            old_bound = (current_score // self.partition_size) * self.partition_size
            new_bound = (new_score // self.partition_size) * self.partition_size

            if user_id in self.user_scores and old_bound != new_bound:
                if old_bound in self.partitions:
                    self.partitions[old_bound].remove_user(user_id)

            self.user_scores[user_id] = new_score
            partition = self._get_partition(new_score)
            partition.update_score(user_id, new_score, timestamp)

    def get_top_k(self, k: int) -> List[LeaderboardEntry]:
        with self.lock:
            result = []
            sorted_bounds = sorted(self.partitions.keys(), reverse=True)
            for bound in sorted_bounds:
                partition = self.partitions[bound]
                remaining = k - len(result)
                if remaining <= 0:
                    break
                result.extend(partition.sorted_entries[:remaining])
            return result

    def get_rank(self, user_id: str) -> int:
        with self.lock:
            score = self.user_scores.get(user_id)
            if score is None:
                return -1

            target_bound = (score // self.partition_size) * self.partition_size
            global_rank = 1

            sorted_bounds = sorted(self.partitions.keys(), reverse=True)
            for bound in sorted_bounds:
                if bound > target_bound:
                    global_rank += len(self.partitions[bound])
                elif bound == target_bound:
                    local_rank = self.partitions[bound].get_rank(user_id)
                    if local_rank != -1:
                        return global_rank + local_rank - 1
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
            
            sorted_bounds = sorted(self.partitions.keys(), reverse=True)
            for bound in sorted_bounds:
                partition = self.partitions[bound]
                for entry in partition.sorted_entries:
                    if min_rank <= current_rank <= max_rank:
                        window.append(entry)
                    if current_rank > max_rank:
                        return window
                    current_rank += 1
            return window

    def get_score(self, user_id: str) -> Optional[int]:
        with self.lock:
            return self.user_scores.get(user_id)

