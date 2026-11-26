import sys
import os

# Dynamic sys.path import to allow tests to run without ModuleNotFoundError
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

import pytest
from content_moderation_platform_service import (
    ContentModerationPlatformService,
    ModerationRequest,
    Action
)


@pytest.fixture
def service():
    blocklist = ["violence", "hate"]
    warnings = ["scam", "suspicious"]
    regexps = [r"\b[a-z]+[0-9]{5,}\b"]
    return ContentModerationPlatformService(
        blocklist_keywords=blocklist,
        warning_keywords=warnings,
        regex_patterns=regexps
    )


def test_clean_content_is_allowed(service):
    request = ModerationRequest(content_id="c1", text="This is a lovely day", surface="feed")
    response = service.evaluate(request)

    assert response.action == Action.ALLOW
    assert response.risk_score < 0.4
    assert response.confidence == 1.0
    assert not response.reasons


def test_blocklist_content_is_removed(service):
    request = ModerationRequest(content_id="c2", text="I love violence and hate", surface="feed")
    response = service.evaluate(request)

    assert response.action == Action.AUTO_REMOVE
    assert response.risk_score >= 0.8
    assert "blocklist_keyword_match: violence" in response.reasons
    assert "blocklist_keyword_match: hate" in response.reasons


def test_warning_content_is_escalated(service):
    request = ModerationRequest(content_id="c3", text="This looks like a scam", media_refs=["img1"], surface="feed")
    response = service.evaluate(request)

    assert response.action == Action.ESCALATE_TO_HUMAN
    assert 0.4 <= response.risk_score < 0.8
    assert "warning_keyword_match: scam" in response.reasons
    assert "media_present" in response.reasons


def test_regex_match_is_removed(service):
    request = ModerationRequest(content_id="c4", text="Check out my link user123456", surface="feed")
    response = service.evaluate(request)

    assert response.action == Action.AUTO_REMOVE
    assert any(r.startswith("regex_match: ") for r in response.reasons)


def test_audit_ledger_and_moderator_decision(service):
    request = ModerationRequest(content_id="c5", text="Some suspicious stuff", surface="feed")
    service.evaluate(request)

    ledger = service.get_audit_ledger()
    assert len(ledger) == 1
    assert ledger[0].content_id == "c5"
    assert ledger[0].final_action == Action.ESCALATE_TO_HUMAN

    service.record_moderator_decision("c5", Action.ALLOW)

    ledger = service.get_audit_ledger()
    assert len(ledger) == 1
    assert ledger[0].final_action == Action.ALLOW
