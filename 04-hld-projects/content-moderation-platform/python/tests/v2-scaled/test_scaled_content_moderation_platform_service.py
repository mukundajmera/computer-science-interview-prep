import pytest
import time
import sys
import os

# To ensure dynamic imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))

from scaled_content_moderation_platform_service import (
    ScaledContentModerationPlatformService, Policy, ModerationRequest, Action
)

@pytest.fixture
def service():
    policy = Policy(version="p2.0", auto_remove_threshold=0.9, escalate_threshold=0.6, demote_threshold=0.4)
    srv = ScaledContentModerationPlatformService(initial_policy=policy, max_workers=4)
    yield srv
    srv.shutdown()

def test_async_fan_out_pipeline(service):
    request = ModerationRequest(
        content_id="c1", text="This is spam", media_refs=["bad_image"], surface="feed"
    )

    future = service.evaluate_async(request)
    response = future.result()

    assert response.action == Action.AUTO_REMOVE
    assert "spam" in response.reasons
    assert "known_bad_media" in response.reasons

def test_priority_reviewer_queue_sla_sorting(service):
    # Adjust policy so hate (0.8) and spam (0.5) both fall into escalate (0.4 to 0.9)
    service.update_policy(Policy("p_test", auto_remove_threshold=0.9, escalate_threshold=0.4, demote_threshold=0.2))

    future1 = service.evaluate_async(ModerationRequest(content_id="c_med", text="spam", surface="feed"))
    future2 = service.evaluate_async(ModerationRequest(content_id="c_high", text="hate", surface="feed"))

    future1.result()
    future2.result()

    task1 = service.get_next_review_task()
    assert task1 is not None
    assert task1.priority == 80 # Hate

    task2 = service.get_next_review_task()
    assert task2 is not None
    assert task2.priority == 50 # Spam

def test_reviewer_conflict_resolution_majority_vote(service):
    service.update_policy(Policy("p_test", auto_remove_threshold=0.9, escalate_threshold=0.4, demote_threshold=0.2))

    future = service.evaluate_async(ModerationRequest(content_id="c1", text="hate", surface="feed"))
    future.result()

    task = service.get_next_review_task()
    assert task is not None
    assert not task.resolved

    resolved = service.submit_review_vote(task.task_id, "rev1", Action.DEMOTE, required_consensus_size=3)
    assert not resolved

    resolved = service.submit_review_vote(task.task_id, "rev2", Action.AUTO_REMOVE, required_consensus_size=3)
    assert not resolved

    resolved = service.submit_review_vote(task.task_id, "rev3", Action.AUTO_REMOVE, required_consensus_size=3)
    assert resolved

    assert task.final_action == Action.AUTO_REMOVE
    assert task.resolved

def test_fast_rollback_policy_cache(service):
    assert service.get_active_policy().version == "p2.0"

    new_policy = Policy("p2.1", 0.95, 0.65, 0.45)
    service.update_policy(new_policy)

    assert service.get_active_policy().version == "p2.1"

    service.rollback_policy("p2.0")
    assert service.get_active_policy().version == "p2.0"

    with pytest.raises(ValueError):
        service.rollback_policy("p_nonexistent")
