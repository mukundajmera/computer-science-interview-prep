import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))
from scaled_bot_detection_platform_service import (
    ScaledBotDetectionPlatformService, Event, RemediationAction
)

@pytest.fixture
def service():
    return ScaledBotDetectionPlatformService()

def test_pass_for_normal_activity(service):
    service.set_ip_reputation("1.2.3.4", 0.1)
    event = Event("user_normal", "login", {"ip": "1.2.3.4", "device_id": "valid_device"}, 1000)

    response = service.evaluate(event)

    assert response.action == RemediationAction.PASS
    assert response.risk_score < 0.4
    assert not response.queued_for_investigation

def test_challenge_silent_pow_for_moderate_risk(service):
    service.set_ip_reputation("1.2.3.5", 0.65)
    event = Event("user_moderate", "login", {"ip": "1.2.3.5", "device_id": "valid"}, 1000)

    response = service.evaluate(event)

    assert response.action == RemediationAction.CHALLENGE_SILENT_POW
    assert "bad_ip_reputation" in response.reasons

def test_challenge_captcha_for_high_risk(service):
    service.set_ip_reputation("1.2.3.6", 1.0)
    event = Event("user_high", "login", {"ip": "1.2.3.6"}, 1000)  # no device_id

    response = service.evaluate(event)

    assert response.action == RemediationAction.CHALLENGE_CAPTCHA
    assert response.queued_for_investigation

    queue = service.get_investigation_queue()
    assert len(queue) == 1
    assert queue[0].account_id == "user_high"

def test_block_and_rate_limit(service):
    service.set_ip_reputation("1.2.3.7", 0.95)

    # Exhaust rate limit
    for i in range(150):
        event = Event("user_spammer", "send_msg", {"ip": "1.2.3.7"}, 1000 + i * 10)
        response = service.evaluate(event)

        if response.action == RemediationAction.BLOCK:
            assert "rate_limited" in response.reasons or response.risk_score >= 0.8
            return

    pytest.fail("Did not trigger block action after rate limit exhaustion")

def test_degraded_rule_only_fallback(service):
    service.set_ml_service_available(False)
    service.set_ip_reputation("1.2.3.8", 0.7)

    event = Event("user_degraded", "login", {"ip": "1.2.3.8"}, 1000)
    response = service.evaluate(event)

    assert "degraded_rule_mode" in response.reasons
    assert response.confidence == 0.4
    assert response.risk_score == 0.7

def test_audit_log_stream(service):
    event = Event("user_audit", "login", {}, 1000)
    service.evaluate(event)

    stream = service.get_audit_log_stream()
    assert len(stream) == 1
    assert stream[0].event.account_id == "user_audit"
