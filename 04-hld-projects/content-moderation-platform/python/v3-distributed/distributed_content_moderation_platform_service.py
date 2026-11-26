import hashlib
import time
import random
import json
import threading
from typing import List, Dict, Optional, Tuple

class ModerationEvent:
    def __init__(self, content_id: str, actor_id: str, text: str, timestamp: int):
        self.content_id = content_id
        self.actor_id = actor_id
        self.text = text
        self.timestamp = timestamp

# 1. Distributed streaming pipeline (Kafka partition mock by actor_id)
class KafkaPartitionMock:
    def __init__(self, num_partitions: int):
        self.num_partitions = num_partitions
        self.partitions: List[List[ModerationEvent]] = [[] for _ in range(num_partitions)]
        self.lock = threading.Lock()

    def publish(self, event: ModerationEvent):
        partition_index = hash(event.actor_id) % self.num_partitions
        with self.lock:
            self.partitions[partition_index].append(event)

    def consume(self, partition_index: int) -> Optional[ModerationEvent]:
        with self.lock:
            if self.partitions[partition_index]:
                return self.partitions[partition_index].pop(0)
            return None


# 2. Multi-region active-active policy cache sync with conflict-free replication (LWW)
class Policy:
    def __init__(self, version: str, remove_threshold: float, timestamp: int):
        self.version = version
        self.remove_threshold = remove_threshold
        self.timestamp = timestamp

class LwwPolicyCache:
    def __init__(self, region: str):
        self.region = region
        self.policies: Dict[str, Policy] = {}
        self.peers: List['LwwPolicyCache'] = []
        self.lock = threading.Lock()

    def add_peer(self, peer: 'LwwPolicyCache'):
        self.peers.append(peer)

    def update_policy(self, category: str, new_policy: Policy):
        self.sync_policy(category, new_policy)
        for peer in self.peers:
            peer.sync_policy(category, new_policy)

    def sync_policy(self, category: str, new_policy: Policy):
        with self.lock:
            current = self.policies.get(category)
            if current is None or new_policy.timestamp > current.timestamp:
                self.policies[category] = new_policy
            elif new_policy.timestamp == current.timestamp and new_policy.version > current.version:
                self.policies[category] = new_policy

    def get_policy(self, category: str) -> Optional[Policy]:
        with self.lock:
            return self.policies.get(category)


# 3. ML inference canary router with shadow traffic evaluation
class InferenceResult:
    def __init__(self, risk_score: float, confidence: float):
        self.risk_score = risk_score
        self.confidence = confidence

class ModelInference:
    def evaluate(self, event: ModerationEvent) -> InferenceResult:
        raise NotImplementedError()

class CanaryRouter:
    def __init__(self, primary_model: ModelInference, canary_model: ModelInference, shadow_traffic_ratio: float):
        self.primary_model = primary_model
        self.canary_model = canary_model
        self.shadow_traffic_ratio = shadow_traffic_ratio
        self.shadow_evaluations: List[str] = []

    def process(self, event: ModerationEvent, force_shadow: bool = False) -> InferenceResult:
        primary_result = self.primary_model.evaluate(event)

        if force_shadow or random.random() < self.shadow_traffic_ratio:
            canary_result = self.canary_model.evaluate(event)
            self._evaluate_shadow(event.content_id, primary_result, canary_result)

        return primary_result

    def _evaluate_shadow(self, content_id: str, primary: InferenceResult, canary: InferenceResult):
        self.shadow_evaluations.append(f"Content {content_id}: Primary({primary.risk_score:.2f}), Canary({canary.risk_score:.2f})")

    def get_shadow_evaluations(self) -> List[str]:
        return self.shadow_evaluations


# 4. Audit compliance immutable ledger
class AuditRecord:
    def __init__(self, content_id: str, action: str, reason: str, timestamp: int, previous_hash: str):
        self.content_id = content_id
        self.action = action
        self.reason = reason
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = self._generate_hash()

    def _generate_hash(self) -> str:
        data = f"{self.content_id}:{self.action}:{self.reason}:{self.timestamp}:{self.previous_hash}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

class AuditLedger:
    def __init__(self):
        self.ledger: List[AuditRecord] = []
        self.last_hash = "0"
        self.lock = threading.Lock()

    def append_record(self, content_id: str, action: str, reason: str, timestamp: int):
        with self.lock:
            record = AuditRecord(content_id, action, reason, timestamp, self.last_hash)
            self.ledger.append(record)
            self.last_hash = record.hash

    def get_records(self) -> List[AuditRecord]:
        with self.lock:
            return list(self.ledger)

    def verify_integrity(self) -> bool:
        with self.lock:
            expected_previous = "0"
            for record in self.ledger:
                if record.previous_hash != expected_previous:
                    return False
                expected_previous = record.hash
            return True

    def tamper_record(self, index: int, new_record: AuditRecord):
        with self.lock:
            if 0 <= index < len(self.ledger):
                self.ledger[index] = new_record
