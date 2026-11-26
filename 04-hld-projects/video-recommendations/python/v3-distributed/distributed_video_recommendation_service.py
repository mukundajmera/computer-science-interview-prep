import time
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import threading

@dataclass
class VideoCandidate:
    video_id: str
    source: str
    base_score: float

    def __hash__(self):
        return hash(self.video_id)

    def __eq__(self, other):
        if not isinstance(other, VideoCandidate):
            return False
        return self.video_id == other.video_id

@dataclass
class RankScore:
    video_id: str
    score: float

class CandidateGenerator:
    def get_candidates(self, user_id: str, context_video_id: str, limit: int) -> List[VideoCandidate]:
        raise NotImplementedError

class RankingShard:
    def rank_candidates(self, user_id: str, candidates: List[VideoCandidate]) -> List[RankScore]:
        raise NotImplementedError

    def get_shard_id(self) -> str:
        raise NotImplementedError

class CircuitBreaker:
    class State:
        CLOSED = 0
        OPEN = 1
        HALF_OPEN = 2

    def __init__(self, failure_threshold: int = 3, reset_timeout_ms: int = 5000):
        self.failure_threshold = failure_threshold
        self.reset_timeout_ms = reset_timeout_ms
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = self.State.CLOSED
        self.lock = threading.Lock()

    def allow_request(self) -> bool:
        with self.lock:
            if self.state == self.State.OPEN:
                if (time.time() * 1000 - self.last_failure_time) > self.reset_timeout_ms:
                    self.state = self.State.HALF_OPEN
                    return True
                return False
            return True

    def record_success(self):
        with self.lock:
            if self.state == self.State.HALF_OPEN:
                self.state = self.State.CLOSED
            self.failures = 0

    def record_failure(self):
        with self.lock:
            self.last_failure_time = time.time() * 1000
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = self.State.OPEN

class DistributedVideoRecommendationService:
    def __init__(self,
                 candidate_generators: List[CandidateGenerator],
                 ranking_shards: List[RankingShard],
                 rank_timeout_ms: int = 250):
        self.candidate_generators = candidate_generators
        self.ranking_shards = ranking_shards
        self.rank_timeout_ms = rank_timeout_ms

        self.shard_circuit_breakers = {
            shard.get_shard_id(): CircuitBreaker(3, 5000)
            for shard in ranking_shards
        }

        # Thread pool for scatter-gather operations
        self.executor = ThreadPoolExecutor(max_workers=16)

        # Real-time feedback storage (simplified)
        self.user_video_scores: Dict[str, Dict[str, float]] = {}
        self.feedback_lock = threading.Lock()

    def record_feedback(self, user_id: str, video_id: str, event_type: str, dwell_ms: float = 0.0):
        # Near-real-time streaming update simulation
        score_delta = 0.0
        if event_type == "CLICK":
            score_delta = 1.0
        elif event_type == "WATCH":
            score_delta = min(10.0, dwell_ms / 1000.0)
        elif event_type == "SKIP":
            score_delta = -2.0
        elif event_type == "LIKE":
            score_delta = 5.0

        with self.feedback_lock:
            if user_id not in self.user_video_scores:
                self.user_video_scores[user_id] = {}
            current_score = self.user_video_scores[user_id].get(video_id, 0.0)
            self.user_video_scores[user_id][video_id] = current_score + score_delta

    def _fetch_candidates_from_generator(self, generator: CandidateGenerator, user_id: str, context_video_id: str, limit: int) -> List[VideoCandidate]:
        try:
            return generator.get_candidates(user_id, context_video_id, limit)
        except Exception:
            return []

    def _rank_partition_with_shard(self, shard: RankingShard, user_id: str, partition: List[VideoCandidate]) -> List[RankScore]:
        shard_id = shard.get_shard_id()
        cb = self.shard_circuit_breakers[shard_id]

        if cb.allow_request():
            try:
                results = shard.rank_candidates(user_id, partition)
                cb.record_success()
                return results
            except Exception as e:
                cb.record_failure()
                raise e
        else:
            # Fallback for tripped circuit breaker: lightweight baseline scoring
            return [RankScore(c.video_id, c.base_score) for c in partition]

    def get_recommendations(self, user_id: str, context_video_id: str, limit: int) -> List[str]:
        # 1. Two-stage candidate retrieval (scatter-gather)
        generator_futures = []
        for generator in self.candidate_generators:
            generator_futures.append(
                self.executor.submit(self._fetch_candidates_from_generator, generator, user_id, context_video_id, limit * 2)
            )

        unique_candidates = set()
        try:
            for future in as_completed(generator_futures, timeout=0.1): # 100ms timeout for generators
                try:
                    candidates = future.result()
                    unique_candidates.update(candidates)
                except Exception:
                    pass
        except TimeoutError:
            pass

        candidates_list = list(unique_candidates)
        if not candidates_list:
            return []

        # 2. Partition candidates across ranking shards
        shards_count = len(self.ranking_shards)
        partitions = [[] for _ in range(shards_count)]
        for i, candidate in enumerate(candidates_list):
            partitions[i % shards_count].append(candidate)

        # 3. Distributed heavy ranking with circuit breaker and timeout
        shard_futures = []
        for i in range(shards_count):
            shard = self.ranking_shards[i]
            partition = partitions[i]
            shard_futures.append(
                (i, self.executor.submit(self._rank_partition_with_shard, shard, user_id, partition))
            )

        final_scores = []
        rank_deadline = time.time() + (self.rank_timeout_ms / 1000.0)

        for i, future in shard_futures:
            time_left = rank_deadline - time.time()
            try:
                if time_left <= 0:
                    raise TimeoutError()
                # Wait for each future with a timeout
                results = future.result(timeout=time_left)
                final_scores.extend(results)
            except TimeoutError:
                # Timeout fallback for this partition
                shard_id = self.ranking_shards[i].get_shard_id()
                self.shard_circuit_breakers[shard_id].record_failure()
                # add fallback scores
                final_scores.extend([RankScore(c.video_id, c.base_score) for c in partitions[i]])
            except Exception:
                # Error fallback
                final_scores.extend([RankScore(c.video_id, c.base_score) for c in partitions[i]])

        # 4. Apply real-time feedback adjustments
        with self.feedback_lock:
            user_adjustments = self.user_video_scores.get(user_id, {})

        for i in range(len(final_scores)):
            rs = final_scores[i]
            adjustment = user_adjustments.get(rs.video_id, 0.0)
            rs.score += adjustment

        # Sort and limit
        final_scores.sort(key=lambda x: x.score, reverse=True)
        return [rs.video_id for rs in final_scores[:limit]]

    def shutdown(self):
        self.executor.shutdown(wait=False)
