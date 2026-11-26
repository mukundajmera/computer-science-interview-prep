import pytest
import sys
import os
from datetime import datetime, timezone

# Add the source directory to the path using dynamic sys.path imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

from content_moderation_service import ContentModerationService, ContentEvent, ModerationStatus

def test_content_moderation_pass():
    service = ContentModerationService(blocklist=["badword"], flag_patterns=[r"\d{3}-\d{2}-\d{4}"])
    event = ContentEvent(content_id="1", author_id="user1", text="Hello world! This is a nice post.")

    result = service.evaluate_content(event)

    assert result.status == ModerationStatus.PASS
    assert len(service.get_review_queue()) == 0

    audit_log = service.get_audit_log()
    assert len(audit_log) == 1
    assert audit_log[0].status == ModerationStatus.PASS

def test_content_moderation_blocked():
    service = ContentModerationService(blocklist=["badword"], flag_patterns=[r"\d{3}-\d{2}-\d{4}"])
    event = ContentEvent(content_id="2", author_id="user2", text="This post contains a badword.")

    result = service.evaluate_content(event)

    assert result.status == ModerationStatus.BLOCKED
    assert "badword" in result.reason
    assert len(service.get_review_queue()) == 0

    audit_log = service.get_audit_log()
    assert len(audit_log) == 1
    assert audit_log[0].status == ModerationStatus.BLOCKED

def test_content_moderation_flagged():
    service = ContentModerationService(blocklist=["badword"], flag_patterns=[r"\d{3}-\d{2}-\d{4}"])
    event = ContentEvent(content_id="3", author_id="user3", text="My SSN is 123-45-6789.")

    result = service.evaluate_content(event)

    assert result.status == ModerationStatus.FLAGGED
    assert "pattern" in result.reason
    assert len(service.get_review_queue()) == 1
    assert service.get_review_queue()[0].content_id == "3"

    audit_log = service.get_audit_log()
    assert len(audit_log) == 1
    assert audit_log[0].status == ModerationStatus.FLAGGED

def test_human_review_process():
    service = ContentModerationService(blocklist=[], flag_patterns=[r"flagme"])
    event1 = ContentEvent(content_id="4", author_id="user4", text="Please flagme here.")
    event2 = ContentEvent(content_id="5", author_id="user5", text="Another flagme post.")

    service.evaluate_content(event1)
    service.evaluate_content(event2)

    assert len(service.get_review_queue()) == 2

    # Process approval
    result_approved = service.process_review("4", approved=True)
    assert result_approved.status == ModerationStatus.PASS
    assert result_approved.reason == "Human review approved"

    # Process rejection
    result_rejected = service.process_review("5", approved=False)
    assert result_rejected.status == ModerationStatus.BLOCKED
    assert result_rejected.reason == "Human review rejected"

    assert len(service.get_review_queue()) == 0

    audit_log = service.get_audit_log()
    assert len(audit_log) == 4 # 2 evaluates, 2 reviews

def test_human_review_not_found():
    service = ContentModerationService()

    with pytest.raises(ValueError, match="not found in review queue"):
        service.process_review("nonexistent_id", approved=True)
