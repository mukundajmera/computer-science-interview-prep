import pytest
import sys
import os

# Add the required path as per memory directive to avoid ImportError
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))

from distributed_content_moderation_service import (
    DistributedContentModerationService,
    Policy,
    ContentEvent,
    ModerationStatus,
    ConsensusNode
)

class MockAcceptNode(ConsensusNode):
    def agree_to_block(self, event, policy):
        return True

class MockRejectNode(ConsensusNode):
    def agree_to_block(self, event, policy):
        return False

@pytest.fixture
def policies():
    p1 = Policy(
        version=1,
        blocklist={"badword"},
        flag_patterns=[r"flag\d+"],
        is_fallback_deterministic=True
    )
    p2 = Policy(
        version=2,
        blocklist={"worseword"},
        flag_patterns=[r"flag\d+"],
        is_fallback_deterministic=False
    )
    return p1, p2

def test_consistent_hash_shard_routing(policies):
    p1, _ = policies
    shards = ["shard-1", "shard-2", "shard-3"]
    service = DistributedContentModerationService(shards, "us-east", p1, [], 1)

    shard_a = service.route_shard("userA")
    shard_b = service.route_shard("userB")
    shard_c = service.route_shard("userC")

    assert shard_a in shards
    assert shard_b in shards
    assert shard_c in shards

    # Consistent routing for the same key
    assert shard_a == service.route_shard("userA")

def test_multi_datacenter_policy_sync(policies):
    p1, p2 = policies
    service = DistributedContentModerationService(["s1"], "us-east", p1, [], 1)

    # Sync a newer policy for the current region
    service.sync_policy("us-east", p2)

    event = ContentEvent("c1", "a1", "this has worseword in it")
    result = service.evaluate_content(event)

    assert result.status == ModerationStatus.BLOCKED
    assert "worseword" in result.reason

def test_distributed_consensus_high_severity(policies):
    p1, _ = policies
    nodes = [MockAcceptNode(), MockAcceptNode(), MockRejectNode()]
    service = DistributedContentModerationService(["s1"], "us-east", p1, nodes, 2)

    event = ContentEvent("c1", "a1", "this is flag123 pattern")
    result = service.evaluate_content(event)

    assert result.status == ModerationStatus.BLOCKED
    assert "Consensus blocked" in result.reason

def test_cluster_partitioning_fallback(policies):
    p1, _ = policies
    nodes = [MockRejectNode(), MockRejectNode()]
    service = DistributedContentModerationService(["s1"], "us-east", p1, nodes, 2)

    event = ContentEvent("c1", "a1", "this is flag123 pattern")

    # Not partitioned -> NEEDS_REVIEW
    result1 = service.evaluate_content(event)
    assert result1.status == ModerationStatus.NEEDS_REVIEW

    # Partitioned -> PASS (because policy1 is_fallback_deterministic = True)
    service.set_partitioned(True)
    result2 = service.evaluate_content(event)
    assert result2.status == ModerationStatus.PASS
    assert "Partition fallback" in result2.reason
