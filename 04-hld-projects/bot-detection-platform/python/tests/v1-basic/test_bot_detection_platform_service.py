import sys
import os
import time

# dynamic path setup
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

from bot_detection_platform_service import BotDetectionPlatformService, Event, RemediationAction

def test_pass_action_for_normal_user():
    service = BotDetectionPlatformService()
    now = int(time.time() * 1000)
    context = {"ip": "192.168.1.1", "device_id": "valid-device-12345"}
    event = Event("user1", "login", context, now)

    response = service.evaluate(event)

    assert response.action == RemediationAction.PASS
    assert response.risk_score < 0.5
    assert not response.queued_for_investigation
    assert len(response.reasons) == 0

def test_challenge_captcha_for_suspicious_ip():
    service = BotDetectionPlatformService()
    service.set_ip_reputation("10.0.0.99", 0.9) # bad IP

    now = int(time.time() * 1000)
    context = {"ip": "10.0.0.99", "device_id": "valid-device-12345"}
    event = Event("user2", "post_comment", context, now)

    response = service.evaluate(event)

    assert response.action == RemediationAction.CHALLENGE_CAPTCHA
    assert 0.5 <= response.risk_score < 0.8
    assert response.queued_for_investigation
    assert "bad_ip_reputation" in response.reasons

    queue = service.get_investigation_queue()
    assert len(queue) == 1
    assert queue[0].account_id == "user2"

def test_block_action_for_bot_behavior():
    service = BotDetectionPlatformService()
    service.set_ip_reputation("10.0.0.99", 1.0) # very bad IP

    now = int(time.time() * 1000)
    context = {"ip": "10.0.0.99", "device_id": ""} # empty device id

    # Simulate high velocity
    for i in range(45):
        event = Event("bot_user", "scraping", context, now - 10000 + i * 100)
        service.ingest_event(event)

    final_event = Event("bot_user", "scraping", context, now)
    response = service.evaluate(final_event)

    assert response.action == RemediationAction.BLOCK
    assert response.risk_score >= 0.8
    assert "bad_ip_reputation" in response.reasons
    assert "device_anomaly" in response.reasons
    assert "velocity_spike" in response.reasons

def test_velocity_spike_alone():
    service = BotDetectionPlatformService()

    now = int(time.time() * 1000)
    context = {"ip": "192.168.1.1", "device_id": "valid-device-12345"}

    # Simulate high velocity (over 50 events/min)
    for i in range(55):
        event = Event("spammer", "send_message", context, now - 50000 + i * 500)
        service.ingest_event(event)

    final_event = Event("spammer", "send_message", context, now)
    response = service.evaluate(final_event)

    assert "velocity_spike" in response.reasons
    assert response.confidence > 0.5
