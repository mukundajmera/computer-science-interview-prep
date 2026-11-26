import json
import threading
import time
import pytest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
for module_name in ["dispatcher", "http_client"]:
    sys.modules.pop(module_name, None)

from dispatcher import WebhookDispatcher, Subscriber, Event
from http_client import HttpClient, DeliveryResult

class MockHttpClient(HttpClient):
    def __init__(self):
        self.calls = []
        self.lock = threading.Lock()
        self.fail_count = 0

    def post(self, url: str, data: str, headers: dict) -> DeliveryResult:
        with self.lock:
            self.calls.append((url, data, headers))
            if self.fail_count > 0:
                self.fail_count -= 1
                return DeliveryResult(500, False)
        return DeliveryResult(200, True)

def test_fast_path_delivery_and_hmac():
    client = MockHttpClient()
    dispatcher = WebhookDispatcher(client, num_workers=2)
    
    sub = Subscriber("sub1", "http://example.com/webhook", "mysecret", "order.*")
    dispatcher.add_subscriber(sub)
    
    event = Event("order.created", {"order_id": 123})
    dispatcher.publish(event)
    
    # Wait for processing
    time.sleep(0.5)
    
    dispatcher.stop()
    
    assert len(client.calls) == 1
    url, data, headers = client.calls[0]
    assert url == "http://example.com/webhook"
    assert json.loads(data) == {"order_id": 123}
    assert 'X-Hub-Signature-256' in headers
    assert headers['X-Hub-Signature-256'].startswith('sha256=')

def test_retry_backoff_and_dlq():
    client = MockHttpClient()
    client.fail_count = 10 # ensure all retries fail
    
    dispatcher = WebhookDispatcher(client, num_workers=2)
    sub = Subscriber("sub1", "http://example.com/fail", "secret", "user.*")
    # speed up testing by overriding base_delay_ms temporarily in tasks if we could, 
    # but we can just wait since max is 3 retries and base is 100ms.
    # Max delay: 1st=200ms, 2nd=400ms, 3rd=800ms. Total ~1.4s
    dispatcher.add_subscriber(sub)
    
    dispatcher.publish(Event("user.created", {"user_id": 1}))
    
    time.sleep(2.0)
    
    dispatcher.stop()
    
    # Initial + 3 retries
    assert len(client.calls) == 4
    
    with dispatcher.dlq_lock:
        assert len(dispatcher.dlq) == 1
        dlq_task = dispatcher.dlq[0]
        assert dlq_task.event.topic == "user.created"
        assert dlq_task.attempt == 4

def test_per_destination_concurrency_limits():
    class DelayHttpClient(HttpClient):
        def __init__(self):
            self.concurrent_requests = 0
            self.max_observed = 0
            self.lock = threading.Lock()
            self.calls = 0

        def post(self, url: str, data: str, headers: dict) -> DeliveryResult:
            with self.lock:
                self.concurrent_requests += 1
                if self.concurrent_requests > self.max_observed:
                    self.max_observed = self.concurrent_requests
            
            time.sleep(0.2)
            
            with self.lock:
                self.concurrent_requests -= 1
                self.calls += 1
            return DeliveryResult(200, True)

    client = DelayHttpClient()
    # 10 workers but dest limit is 3
    dispatcher = WebhookDispatcher(client, num_workers=10, max_concurrent_per_dest=3)
    
    sub = Subscriber("sub1", "http://slow.com/hook", "secret", "batch.*")
    dispatcher.add_subscriber(sub)
    
    for i in range(10):
        dispatcher.publish(Event(f"batch.{i}", {"id": i}))
        
    time.sleep(3.0)
    dispatcher.stop()
    
    assert client.calls == 10
    assert client.max_observed <= 3
    assert client.max_observed > 0

def test_multiple_subscribers():
    client = MockHttpClient()
    dispatcher = WebhookDispatcher(client, num_workers=2)
    
    dispatcher.add_subscriber(Subscriber("sub1", "http://sub1.com", "secret", "event.*"))
    dispatcher.add_subscriber(Subscriber("sub2", "http://sub2.com", "secret", "event.specific"))
    dispatcher.add_subscriber(Subscriber("sub3", "http://sub3.com", "secret", "other.*"))
    
    dispatcher.publish(Event("event.specific", {"val": 1}))
    
    time.sleep(0.5)
    dispatcher.stop()
    
    assert len(client.calls) == 2
    urls = [call[0] for call in client.calls]
    assert "http://sub1.com" in urls
    assert "http://sub2.com" in urls
    assert "http://sub3.com" not in urls

def test_no_match_topic():
    client = MockHttpClient()
    dispatcher = WebhookDispatcher(client, num_workers=2)
    
    sub = Subscriber("sub_nomatch", "http://example.com/nomatch", "mysecret", "nomatch.*")
    dispatcher.add_subscriber(sub)
    
    event = Event("user.created", {"user_id": 456})
    dispatcher.publish(event)
    
    time.sleep(0.5)
    dispatcher.stop()
    
    assert len(client.calls) == 0
