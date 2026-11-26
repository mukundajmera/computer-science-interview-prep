import threading
import time
from typing import Dict, List, Set, Optional

class ConsumerGroupCoordinator:
    def __init__(self, heartbeat_timeout: float = 5.0):
        self.heartbeat_timeout = heartbeat_timeout
        # group_id -> dict of member_id -> last_heartbeat
        self.members: Dict[str, Dict[str, float]] = {}
        # group_id -> dict of partition_id -> member_id
        self.assignments: Dict[str, Dict[str, str]] = {}
        # group_id -> list of partition_ids
        self.group_partitions: Dict[str, List[str]] = {}
        # group_id -> dict of partition_id -> offset
        self.committed_offsets: Dict[str, Dict[str, int]] = {}
        self.lock = threading.RLock()

    def register_group(self, group_id: str, partitions: List[str]):
        with self.lock:
            if group_id not in self.members:
                self.members[group_id] = {}
                self.assignments[group_id] = {}
                self.group_partitions[group_id] = partitions
                self.committed_offsets[group_id] = {}

    def join_group(self, group_id: str, member_id: str):
        with self.lock:
            if group_id not in self.members:
                self.members[group_id] = {}
            self.members[group_id][member_id] = time.time()
            self._rebalance(group_id)

    def heartbeat(self, group_id: str, member_id: str):
        with self.lock:
            if group_id in self.members and member_id in self.members[group_id]:
                self.members[group_id][member_id] = time.time()

    def check_health(self):
        with self.lock:
            now = time.time()
            for group_id, members in list(self.members.items()):
                dead_members = [m_id for m_id, last_hb in members.items() if now - last_hb > self.heartbeat_timeout]
                if dead_members:
                    for m_id in dead_members:
                        del members[m_id]
                    self._rebalance(group_id)

    def _rebalance(self, group_id: str):
        # Range assignment strategy
        members = sorted(list(self.members.get(group_id, {}).keys()))
        partitions = sorted(self.group_partitions.get(group_id, []))
        
        self.assignments[group_id] = {}
        
        if not members or not partitions:
            return
            
        partitions_per_member = len(partitions) // len(members)
        extra = len(partitions) % len(members)
        
        p_idx = 0
        for i, m_id in enumerate(members):
            count = partitions_per_member + (1 if i < extra else 0)
            for _ in range(count):
                self.assignments[group_id][partitions[p_idx]] = m_id
                p_idx += 1

    def get_assignment(self, group_id: str, member_id: str) -> List[str]:
        with self.lock:
            assignment = self.assignments.get(group_id, {})
            return [p for p, m in assignment.items() if m == member_id]

    def commit_offset(self, group_id: str, partition_id: str, offset: int):
        with self.lock:
            if group_id not in self.committed_offsets:
                self.committed_offsets[group_id] = {}
            self.committed_offsets[group_id][partition_id] = offset

    def fetch_offset(self, group_id: str, partition_id: str) -> int:
        with self.lock:
            group_offsets = self.committed_offsets.get(group_id, {})
            return group_offsets.get(partition_id, 0)

