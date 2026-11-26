import sys
import os
import time
import threading
import pytest

# Add v1-simple to sys.path to allow importing without a package prefix
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from idempotency_key_manager import IdempotencyKeyManager, Status, ConflictException, InProgressException

@pytest.fixture
def manager():
    return IdempotencyKeyManager(ttl_seconds=0.1)  # 100ms TTL for testing

def test_new_request_and_completion(manager):
    key = "key1"
    payload = "payload1"

    record = manager.begin_request(key, payload)
    assert record.status == Status.IN_PROGRESS
    assert record.response is None

    manager.complete_request(key, "response1")

    record2 = manager.begin_request(key, payload)
    assert record2.status == Status.COMPLETED
    assert record2.response == "response1"

def test_conflict_on_different_payload(manager):
    key = "key2"
    manager.begin_request(key, "payloadA")

    with pytest.raises(ConflictException):
        manager.begin_request(key, "payloadB")

def test_failed_request(manager):
    key = "key3"
    manager.begin_request(key, "payload3")
    manager.fail_request(key)

    record = manager.begin_request(key, "payload3")
    assert record.status == Status.FAILED

def test_expired_request_replaced(manager):
    key = "key4"
    manager.begin_request(key, "payload4")

    time.sleep(0.15)  # Wait for TTL to expire

    # After expiration, a new request with the same key should succeed
    record = manager.begin_request(key, "payload5")
    assert record.status == Status.IN_PROGRESS

def test_cleanup(manager):
    manager.begin_request("key5", "payload5")
    time.sleep(0.15)
    manager.cleanup()

    # Key should be gone, we can start fresh
    record = manager.begin_request("key5", "payload6")
    assert record.status == Status.IN_PROGRESS

def test_in_progress_concurrent_rejection(manager):
    key = "key6"
    manager.begin_request(key, "payload6")

    # A subsequent call with the same payload before completion should throw InProgressException
    with pytest.raises(InProgressException):
        manager.begin_request(key, "payload6")
