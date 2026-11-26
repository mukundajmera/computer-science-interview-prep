import hashlib
import time
from enum import Enum
from typing import List, Dict, Optional, Set
from urllib.parse import urlparse
from dataclasses import dataclass, field
import queue
import threading

class JobStatus(Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"

@dataclass
class CrawlJob:
    id: str
    seeds: List[str]
    domain_scope: str
    status: JobStatus = JobStatus.RUNNING

@dataclass(order=True)
class FrontierItem:
    priority: int
    url: str = field(compare=False)

class TokenBucket:
    def __init__(self, capacity: int, refill_rate_per_second: int):
        self.capacity = capacity
        self.refill_rate_per_second = refill_rate_per_second
        self.tokens = float(capacity)
        self.last_refill_timestamp = time.time()
        self.lock = threading.Lock()

    def try_consume(self) -> bool:
        with self.lock:
            self._refill()
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return True
            return False

    def _refill(self):
        now = time.time()
        time_passed_seconds = now - self.last_refill_timestamp
        tokens_to_add = time_passed_seconds * self.refill_rate_per_second
        self.tokens = min(float(self.capacity), self.tokens + tokens_to_add)
        self.last_refill_timestamp = now

class ScaledWebCrawlerService:
    def __init__(self):
        self.jobs: Dict[str, CrawlJob] = {}
        self.frontier: queue.PriorityQueue = queue.PriorityQueue()
        self.seen_urls: Set[str] = set()
        self.seen_content_hashes: Set[str] = set()
        self.host_buckets: Dict[str, TokenBucket] = {}
        self.default_bucket_capacity = 5
        self.default_refill_rate = 1
        self.lock = threading.Lock()

    def create_job(self, job_id: str, seeds: List[str], domain_scope: str) -> CrawlJob:
        job = CrawlJob(id=job_id, seeds=seeds, domain_scope=domain_scope)
        self.jobs[job_id] = job
        for seed in seeds:
            self.add_url_to_frontier(seed, 10, domain_scope)
        return job

    def pause_job(self, job_id: str):
        if job_id in self.jobs:
            self.jobs[job_id].status = JobStatus.PAUSED

    def resume_job(self, job_id: str):
        if job_id in self.jobs:
            self.jobs[job_id].status = JobStatus.RUNNING

    def get_job_status(self, job_id: str) -> Optional[JobStatus]:
        job = self.jobs.get(job_id)
        return job.status if job else None

    def _is_within_scope(self, url_str: str, domain_scope: str) -> bool:
        if not domain_scope:
            return True
        try:
            parsed = urlparse(url_str)
            host = parsed.hostname
            if not host:
                return False
            return host == domain_scope or host.endswith("." + domain_scope)
        except Exception:
            return False

    def add_url_to_frontier(self, url: str, priority: int, domain_scope: str) -> bool:
        if not self._is_within_scope(url, domain_scope):
            return False

        with self.lock:
            if url not in self.seen_urls:
                self.seen_urls.add(url)
                self.frontier.put(FrontierItem(priority=priority, url=url))
                return True
            return False

    def generate_content_fingerprint(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def is_duplicate_content(self, content: str) -> bool:
        content_hash = self.generate_content_fingerprint(content)
        with self.lock:
            if content_hash in self.seen_content_hashes:
                return True
            self.seen_content_hashes.add(content_hash)
            return False

    def get_host(self, url_str: str) -> Optional[str]:
        try:
            return urlparse(url_str).hostname
        except Exception:
            return None

    def try_fetch(self, url_str: str) -> bool:
        host = self.get_host(url_str)
        if not host:
            return False

        with self.lock:
            if host not in self.host_buckets:
                self.host_buckets[host] = TokenBucket(self.default_bucket_capacity, self.default_refill_rate)
            bucket = self.host_buckets[host]

        return bucket.try_consume()

    def poll_frontier(self) -> Optional[FrontierItem]:
        try:
            return self.frontier.get_nowait()
        except queue.Empty:
            return None

    def get_frontier_size(self) -> int:
        return self.frontier.qsize()
