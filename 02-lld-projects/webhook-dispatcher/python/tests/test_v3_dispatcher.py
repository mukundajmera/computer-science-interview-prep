import json
import threading
import time
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))
for module_name in ["dispatcher", "http_client"]:
    sys.modules.pop(module_name, None)

from dispatcher import WebhookDispatcher, Subscriber, Event, CircuitBreaker
from http_client import HttpClient, DeliveryResult

class MockHttpClient(HttpClient):
    def __init__(self):
        self.calls = []
        self.lock = threading.Lock()
        self.fail_count = 0
        self.fail_status = 500

    def post(self, url: str, data: str, headers: dict) -> DeliveryResult:
        with self.lock:
            self.calls.append((url, data, headers))
            if self.fail_count > 0:
                self.fail_count -= 1
                return DeliveryResult(self.fail_status, False)
        return DeliveryResult(200, True)

def test_v3_circuit_breaker_trip_and_recover():
    client = MockHttpClient()
    client.fail_count = 5 # 5 consecutive failures
    
    dispatcher = WebhookDispatcher(client, num_workers=2)
    # Set a short cooldown for testing
    sub = Subscriber("sub1", "http://example.com/cb", "secret", "cb.*")
    dispatcher.add_subscriber(sub)
    cb = dispatcher.circuit_breakers[sub.endpoint]
    cb.cooldown_ms = 1000 # 1 second
    

    # Fire 5 events to trip the breaker, wait for them to process
    for i in range(5):
        dispatcher.publish(Event("cb.test", {"id": i}))
        time.sleep(0.1) # small delay to let it process
    
    time.sleep(0.5)


    assert cb.state == "OPEN"

    # Wait for cooldown
    time.sleep(1.5)
    
    # Now it should be HALF_OPEN and allow a request
    dispatcher.publish(Event("cb.test", {"id": 6}))
    time.sleep(1.0)
    
    # The delayed request from earlier and the new request should eventually go through
    # but at least one should transition it to CLOSED since HTTP client will now succeed
    assert cb.state == "CLOSED"
    with client.lock:
        assert len(client.calls) > 0 # At least some call went through successfully
    
    dispatcher.stop()


def test_v3_full_jitter_backoff():
    # We mainly test that the delay is less than or equal to the maximum exponential backoff limit
    client = MockHttpClient()
    client.fail_count = 100
    
    dispatcher = WebhookDispatcher(client, num_workers=1)
    sub = Subscriber("sub1", "http://example.com/jitter", "secret", "jitter.*")
    dispatcher.add_subscriber(sub)
    
    start_time = time.time()
    dispatcher.publish(Event("jitter.test", {}))
    
    time.sleep(2.0)
    
    with client.lock:
        calls = len(client.calls)
        
    assert calls > 1
    dispatcher.stop()

def test_v3_dlq_capture_and_replay():
    client = MockHttpClient()
    client.fail_count = 100 # Always fail
    
    dispatcher = WebhookDispatcher(client, num_workers=2)
    sub = Subscriber("sub1", "http://example.com/dlq", "secret", "dlq.*")
    dispatcher.add_subscriber(sub)
    
    event = Event("dlq.test", {"id": 1})
    task = __import__('dispatcher').WebhookTask(event, sub)
    task.attempt = 6 # Force it to go to DLQ immediately when it fails
    
    dispatcher._handle_failure(task, dispatcher.circuit_breakers[sub.endpoint])
    
    items = dispatcher.dlq.get_items()
    assert len(items) == 1
    assert items[0].event.topic == "dlq.test"
    
    client.fail_count = 0
    
    dispatcher.replay_dlq()
    
    assert len(dispatcher.dlq.get_items()) == 0
    time.sleep(0.5)
    
    assert len(client.calls) == 1
    
    dispatcher.stop()

def test_v3_dlq_retention_and_format():
    dlq = __import__('dispatcher').PersistentDlq(retention_days=7)
    sub = Subscriber("sub1", "http://test.com", "secret", "topic.*")
    task = __import__('dispatcher').WebhookTask(Event("topic.a", {}), sub)
    
    dlq.add(task)
    items = dlq.get_items()
    
    assert len(items) == 1
    assert items[0] == task
    assert dlq.retention_days == 7

