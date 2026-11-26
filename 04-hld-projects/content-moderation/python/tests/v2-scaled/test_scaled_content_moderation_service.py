import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))
from scaled_content_moderation_service import (
    ScaledContentModerationService, ContentEvent, ModerationStatus, MLModelService
)

class MockMLService(MLModelService):
    def __init__(self):
        self.should_fail = False
        self.harmful_response = (False, 1.0, "safe")

    def predict(self, text: str):
        if self.should_fail:
            raise TimeoutError("ML service timeout")
        return self.harmful_response

@pytest.fixture
def ml_service():
    return MockMLService()

@pytest.fixture
def service(ml_service):
    return ScaledContentModerationService(
        blocklist=["badword"],
        flag_patterns=[r"\bviagra\b"],
        ml_service=ml_service,
        review_consensus_threshold=2,
        max_queue_size=2
    )

def test_tier1_fast_path_block(service):
    event = ContentEvent("1", "u1", "This is a badword.")
    result = service.evaluate_content(event)
    assert result.status == ModerationStatus.BLOCKED
    assert "Blocked keyword" in result.reason

def test_tier2_ml_high_confidence_block(service, ml_service):
    ml_service.harmful_response = (True, 0.95, "hate_speech")
    event = ContentEvent("2", "u1", "This text is fine to tier1")
    result = service.evaluate_content(event)
    assert result.status == ModerationStatus.BLOCKED
    assert "ML blocked" in result.reason

def test_tier2_degraded_mode_timeout(service, ml_service):
    ml_service.should_fail = True
    event = ContentEvent("3", "u1", "Some normal text")
    result = service.evaluate_content(event)
    assert result.status == ModerationStatus.PASS
    assert "Degraded mode" in result.reason

def test_queue_backpressure(service, ml_service):
    ml_service.harmful_response = (True, 0.75, "spam")

    # Fill queue
    event1 = ContentEvent("q1", "u1", "Suspicious 1")
    service.evaluate_content(event1)

    event2 = ContentEvent("q2", "u1", "Suspicious 2")
    service.evaluate_content(event2)

    assert len(service.review_queue) == 2

    # Exceed queue
    event3 = ContentEvent("q3", "u1", "Suspicious 3")
    result = service.evaluate_content(event3)

    # Should degrade to pass
    assert result.status == ModerationStatus.PASS
    assert "Queue full" in result.reason

def test_appeals_consensus_workflow(service, ml_service):
    ml_service.harmful_response = (True, 0.75, "spam")
    event = ContentEvent("a1", "u1", "Please review me")
    result = service.evaluate_content(event)
    assert result.status == ModerationStatus.NEEDS_REVIEW

    # First reviewer approves
    service.process_review("a1", True)
    assert "a1" in service.review_queue

    # Second reviewer approves (meets consensus threshold = 2)
    final_result = service.process_review("a1", True)
    assert final_result is not None
    assert final_result.status == ModerationStatus.PASS
    assert "consensus: approved" in final_result.reason
    assert "a1" not in service.review_queue

def test_appeals_consensus_rejection(service, ml_service):
    ml_service.harmful_response = (True, 0.75, "spam")
    event = ContentEvent("a2", "u1", "Please review me again")
    service.evaluate_content(event)

    # First reviewer rejects
    service.process_review("a2", False)
    assert "a2" in service.review_queue

    # Second reviewer rejects
    final_result = service.process_review("a2", False)
    assert final_result is not None
    assert final_result.status == ModerationStatus.BLOCKED
    assert "consensus: rejected" in final_result.reason
    assert "a2" not in service.review_queue
