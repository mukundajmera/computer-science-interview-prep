import pytest
import time
import sys
import os

# Adjust path to find the module properly due to hyphenated directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))

from distributed_bot_detection_platform_service import (
    DistributedBotDetectionPlatformService,
    Event,
    RemediationAction
)


@pytest.fixture
def service():
    return DistributedBotDetectionPlatformService("node-1", ["node-1", "node-2", "node-3"])


def test_shadow_mode_evaluation(service):
    service.set_shadow_mode_enabled(True)
    service.set_ml_service_available(False)
    service.update_global_ip_reputation("192.168.1.1", 1.0)

    context = {"ip": "192.168.1.1", "device_id": "12345"}
    event = Event("acc-1", "login", context, int(time.time() * 1000))

    response = service.evaluate(event)

    assert response.action == RemediationAction.SHADOW_BLOCK
    assert "bad_ip_reputation" in response.reasons


def test_bloom_filter_and_redis_ip_reputation(service):
    service.set_ml_service_available(False)
    service.update_global_ip_reputation("10.0.0.1", 0.9)

    context = {"ip": "10.0.0.1", "device_id": "12345"}
    event = Event("acc-2", "login", context, int(time.time() * 1000))

    response = service.evaluate(event)
    assert response.action == RemediationAction.BLOCK
    assert "bad_ip_reputation" in response.reasons

    service.update_global_ip_reputation("10.0.0.1", 0.1)

    context2 = {"ip": "10.0.0.1", "device_id": "12345"}
    event2 = Event("acc-3", "login", context2, int(time.time() * 1000))

    response2 = service.evaluate(event2)
    assert response2.action == RemediationAction.PASS


def test_kafka_audit_telemetry_sink(service):
    context = {"ip": "172.16.0.1", "device_id": "12345"}
    event = Event("acc-4", "login", context, int(time.time() * 1000))

    service.evaluate(event)
    service.evaluate(event)

    assert len(service.kafka_audit_telemetry_sink) == 2
    assert service.kafka_audit_telemetry_sink[0].event.account_id == "acc-4"


def test_cluster_consensus(service):
    assert service.check_cluster_consensus() is True

    minority_service = DistributedBotDetectionPlatformService("node-1", ["node-1"])
    assert minority_service.check_cluster_consensus() is True


def test_rate_limiting_triggers_block(service):
    context = {"ip": "172.16.0.2", "device_id": "12345678"}
    now = int(time.time() * 1000)

    for i in range(100):
        event = Event("acc-spam", "login", context, now + i)
        service.evaluate(event)

    final_event = Event("acc-spam", "login", context, now + 100)
    response = service.evaluate(final_event)

    assert response.action == RemediationAction.BLOCK
    assert "rate_limited" in response.reasons
