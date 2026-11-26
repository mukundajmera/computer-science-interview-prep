import hashlib
from enum import Enum
from typing import Dict, List, Set, Optional, Callable


class JobState(Enum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"


class JobRun:
    def __init__(self, job_id: str, scheduled_at: int):
        self.job_id = job_id
        self.scheduled_at = scheduled_at
        self.lease_owner: Optional[str] = None
        self.lease_until: int = 0
        self.attempt: int = 0
        self.state: JobState = JobState.SCHEDULED
        self.idempotency_token: str = f"{job_id}-{scheduled_at}"


class Datastore:
    def __init__(self):
        self.leader_id: Optional[str] = None
        self.leader_lease_until: int = 0
        self.heartbeats: Dict[str, int] = {}
        self.jobs: Dict[str, JobRun] = {}
        self.completed_tokens: Set[str] = set()

    def try_acquire_leader(self, node_id: str, current_time: int, lease_duration: int) -> bool:
        if self.leader_id is None or current_time >= self.leader_lease_until:
            self.leader_id = node_id
            self.leader_lease_until = current_time + lease_duration
            return True
        if node_id == self.leader_id:
            self.leader_lease_until = current_time + lease_duration
            return True
        return False

    def heartbeat(self, node_id: str, current_time: int):
        self.heartbeats[node_id] = current_time

    def get_active_nodes(self, current_time: int, timeout: int) -> List[str]:
        return sorted([node for node, last_hb in self.heartbeats.items() if current_time - last_hb <= timeout])

    def submit_job(self, job_id: str, scheduled_at: int):
        if job_id not in self.jobs:
            self.jobs[job_id] = JobRun(job_id, scheduled_at)

    def get_job(self, job_id: str) -> Optional[JobRun]:
        return self.jobs.get(job_id)


class ConsistentHashRing:
    def __init__(self):
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        self.virtual_nodes = 5

    def update_ring(self, nodes: List[str]):
        self.ring.clear()
        self.sorted_keys.clear()
        for node in nodes:
            for i in range(self.virtual_nodes):
                key = f"{node}-vn-{i}"
                hashed_key = self._hash(key)
                self.ring[hashed_key] = node
        self.sorted_keys = sorted(self.ring.keys())

    def get_node(self, key: str) -> Optional[str]:
        if not self.sorted_keys:
            return None
        hashed_key = self._hash(key)
        for ring_key in self.sorted_keys:
            if hashed_key <= ring_key:
                return self.ring[ring_key]
        return self.ring[self.sorted_keys[0]]

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) & 0xffffffff


class DistributedJobScheduler:
    def __init__(self, node_id: str, datastore: Datastore, handler: Callable[[str, str], bool]):
        self.node_id = node_id
        self.datastore = datastore
        self.handler = handler
        self.ring = ConsistentHashRing()
        self.is_leader = False

    def get_node_id(self) -> str:
        return self.node_id

    def tick(self, now: int):
        self.datastore.heartbeat(self.node_id, now)
        self.is_leader = self.datastore.try_acquire_leader(self.node_id, now, 5000)

        if self.is_leader:
            self._manage_cluster(now)

        self._process_jobs(now)

    def _manage_cluster(self, now: int):
        active_nodes = self.datastore.get_active_nodes(now, 5000)
        self.ring.update_ring(active_nodes)

        for run in self.datastore.jobs.values():
            if run.state == JobState.SCHEDULED and run.scheduled_at <= now:
                self._assign_job(run, now)
            elif run.state == JobState.RUNNING and now >= run.lease_until:
                self._assign_job(run, now)
            elif run.state == JobState.FAILED:
                self._assign_job(run, now)

    def _assign_job(self, run: JobRun, now: int):
        target_node = self.ring.get_node(run.job_id)
        if target_node:
            run.attempt += 1
            if run.attempt > 3:
                run.state = JobState.DEAD_LETTER
            else:
                run.lease_owner = target_node
                run.lease_until = now + 10000
                run.state = JobState.RUNNING

    def _process_jobs(self, now: int):
        my_jobs = []
        for run in self.datastore.jobs.values():
            if run.state == JobState.RUNNING and self.node_id == run.lease_owner and now < run.lease_until:
                my_jobs.append(run)

        for run in my_jobs:
            if run.idempotency_token in self.datastore.completed_tokens:
                run.state = JobState.COMPLETED
                continue

            try:
                success = self.handler(run.job_id, run.idempotency_token)
                if success:
                    run.state = JobState.COMPLETED
                    self.datastore.completed_tokens.add(run.idempotency_token)
                else:
                    run.state = JobState.FAILED
                    run.lease_until = 0
            except Exception:
                run.state = JobState.FAILED
                run.lease_until = 0
