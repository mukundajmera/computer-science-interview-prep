import pytest
import sys
import os

# Adjust path to import correctly from v3-distributed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))

from distributed_content_moderation_platform_service import (
    ModerationEvent, KafkaPartitionMock, LwwPolicyCache, Policy,
    CanaryRouter, ModelInference, InferenceResult, AuditLedger, AuditRecord
)

def test_kafka_partition_mock():
    kafka = KafkaPartitionMock(num_partitions=3)

    event1 = ModerationEvent(content_id="c1", actor_id="actor1", text="text1", timestamp=100)
    event2 = ModerationEvent(content_id="c2", actor_id="actor2", text="text2", timestamp=101)

    kafka.publish(event1)
    kafka.publish(event2)

    p1 = hash("actor1") % 3
    p2 = hash("actor2") % 3

    assert kafka.consume(p1) == event1
    assert kafka.consume(p2) == event2
    assert kafka.consume(p1) is None

def test_lww_policy_cache_replication_and_conflict_resolution():
    us_east = LwwPolicyCache("us-east")
    eu_west = LwwPolicyCache("eu-west")

    us_east.add_peer(eu_west)
    eu_west.add_peer(us_east)

    # Concurrent update with different timestamps
    p1 = Policy(version="v1", remove_threshold=0.9, timestamp=1000)
    us_east.update_policy("violence", p1)

    assert us_east.get_policy("violence").remove_threshold == 0.9
    assert eu_west.get_policy("violence").remove_threshold == 0.9

    # Conflict: older timestamp should be ignored
    p_old = Policy(version="v0", remove_threshold=0.8, timestamp=900)
    eu_west.update_policy("violence", p_old)

    assert us_east.get_policy("violence").remove_threshold == 0.9
    assert eu_west.get_policy("violence").remove_threshold == 0.9

    # Conflict: same timestamp, higher version string wins
    p_tie_breaker = Policy(version="v2", remove_threshold=0.95, timestamp=1000)
    eu_west.update_policy("violence", p_tie_breaker)

    assert us_east.get_policy("violence").remove_threshold == 0.95
    assert eu_west.get_policy("violence").remove_threshold == 0.95

class MockModel(ModelInference):
    def __init__(self, risk_score, confidence):
        self.risk_score = risk_score
        self.confidence = confidence

    def evaluate(self, event):
        return InferenceResult(self.risk_score, self.confidence)

def test_canary_router_shadow_traffic():
    primary = MockModel(0.8, 0.9)
    canary = MockModel(0.85, 0.92)

    router = CanaryRouter(primary, canary, shadow_traffic_ratio=0.0)
    event = ModerationEvent("c1", "a1", "test", 1)

    # No shadow
    router.process(event, force_shadow=False)
    assert len(router.get_shadow_evaluations()) == 0

    # Force shadow
    result = router.process(event, force_shadow=True)
    assert result.risk_score == 0.8
    assert len(router.get_shadow_evaluations()) == 1

    evaluation = router.get_shadow_evaluations()[0]
    assert "Primary(0.80)" in evaluation
    assert "Canary(0.85)" in evaluation

def test_audit_ledger_integrity():
    ledger = AuditLedger()

    ledger.append_record("c1", "remove", "violence", 100)
    ledger.append_record("c2", "demote", "spam", 101)

    assert ledger.verify_integrity() is True

    records = ledger.get_records()
    assert len(records) == 2

    # Tamper with the ledger
    original = records[0]
    tampered = AuditRecord(
        content_id=original.content_id,
        action="allow",
        reason="tampered",
        timestamp=original.timestamp,
        previous_hash=original.previous_hash
    )

    ledger.tamper_record(0, tampered)

    # Integrity check should fail because the next record's previous_hash won't match the tampered record's hash
    assert ledger.verify_integrity() is False
