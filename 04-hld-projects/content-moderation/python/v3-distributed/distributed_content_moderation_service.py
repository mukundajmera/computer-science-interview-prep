from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Set
import re
import hashlib

class ModerationStatus:
    PASS = "PASS"
    FLAGGED = "FLAGGED"
    BLOCKED = "BLOCKED"
    NEEDS_REVIEW = "NEEDS_REVIEW"

class ContentEvent:
    def __init__(self, content_id: str, author_id: str, text: str, created_at: Optional[datetime] = None):
        self.content_id = content_id
        self.author_id = author_id
        self.text = text
        self.created_at = created_at if created_at else datetime.now(timezone.utc)

class ModerationResult:
    def __init__(self, content_id: str, status: str, reason: str, confidence: float = 1.0, shard_id: str = "default-shard"):
        self.content_id = content_id
        self.status = status
        self.reason = reason
        self.confidence = confidence
        self.shard_id = shard_id
        self.decided_at = datetime.now(timezone.utc)

class Policy:
    def __init__(self, version: int, blocklist: Set[str], flag_patterns: List[str], is_fallback_deterministic: bool):
        self.version = version
        self.blocklist = set(w.lower() for w in blocklist) if blocklist else set()
        self.flag_patterns = [re.compile(p) for p in flag_patterns] if flag_patterns else []
        self.is_fallback_deterministic = is_fallback_deterministic

class ConsensusNode:
    def agree_to_block(self, event: ContentEvent, policy: Policy) -> bool:
        pass

class DistributedContentModerationService:
    def __init__(self,
                 shards: List[str],
                 current_region: str,
                 initial_policy: Policy,
                 consensus_nodes: List[ConsensusNode],
                 consensus_threshold: int):
        self.current_region = current_region
        self.active_policy = initial_policy
        self.consensus_nodes = consensus_nodes if consensus_nodes else []
        self.consensus_threshold = consensus_threshold

        self.hash_ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []

        if shards:
            for shard in shards:
                for i in range(3): # 3 virtual nodes per shard
                    key = self._hash(f"{shard}:{i}")
                    self.hash_ring[key] = shard
            self.sorted_keys = sorted(self.hash_ring.keys())

        self.region_policies: Dict[str, Policy] = {}
        self.is_partitioned = False

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def route_shard(self, routing_key: str) -> str:
        if not self.hash_ring:
            return "default-shard"

        h = self._hash(routing_key)
        for k in self.sorted_keys:
            if h <= k:
                return self.hash_ring[k]

        return self.hash_ring[self.sorted_keys[0]]

    def sync_policy(self, region: str, policy: Policy):
        self.region_policies[region] = policy
        if self.current_region == region or region == "global":
            if self.active_policy is None or policy.version > self.active_policy.version:
                self.active_policy = policy

    def set_partitioned(self, partitioned: bool):
        self.is_partitioned = partitioned

    def evaluate_content(self, event: ContentEvent) -> ModerationResult:
        shard_id = self.route_shard(event.author_id)
        text_lower = event.text.lower()

        policy = self.active_policy
        if policy is None:
            return ModerationResult(event.content_id, ModerationStatus.PASS, "No active policy", 0.0, shard_id)

        # Fast deterministic checks
        for word in policy.blocklist:
            if word in text_lower:
                return ModerationResult(event.content_id, ModerationStatus.BLOCKED, f"Deterministic block: {word}", 1.0, shard_id)

        flagged = False
        flag_reason = None
        for pattern in policy.flag_patterns:
            if pattern.search(event.text):
                flagged = True
                flag_reason = f"Flagged by pattern: {pattern.pattern}"
                break

        if flagged:
            if self.is_partitioned:
                # Cluster partitioning fallback: use high-precision deterministic rules
                if policy.is_fallback_deterministic:
                    return ModerationResult(event.content_id, ModerationStatus.PASS, "Partition fallback: bypassed flag", 0.0, shard_id)
                else:
                    return ModerationResult(event.content_id, ModerationStatus.NEEDS_REVIEW, f"Partition fallback: {flag_reason}", 0.5, shard_id)

            # Distributed consensus for high-severity
            approvals = sum(1 for node in self.consensus_nodes if node.agree_to_block(event, policy))

            if approvals >= self.consensus_threshold:
                return ModerationResult(event.content_id, ModerationStatus.BLOCKED, "Consensus blocked", 0.9, shard_id)

            return ModerationResult(event.content_id, ModerationStatus.NEEDS_REVIEW, flag_reason, 0.8, shard_id)

        return ModerationResult(event.content_id, ModerationStatus.PASS, "Passed all checks", 1.0, shard_id)
