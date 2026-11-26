import json
import threading
import time
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))
for module_name in ["dispatcher", "http_client"]:
    sys.modules.pop(module_name, None)

from dispatcher import WebhookDispatcher, Subscriber, Event, generate_signature, verify_signature
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

def test_v2_fast_path_delivery_and_hmac_with_timestamp():
    client = MockHttpClient()
    dispatcher = WebhookDispatcher(client, num_workers=2)
    
    sub = Subscriber("sub1", "http://example.com/webhook", "mysecret", "order.*")
    dispatcher.add_subscriber(sub)
    
    event = Event("order.created", {"order_id": 123})
    dispatcher.publish(event)
    
    time.sleep(0.5)
    dispatcher.stop()
    
    assert len(client.calls) == 1
    url, data, headers = client.calls[0]
    assert url == "http://example.com/webhook"
    assert json.loads(data) == {"order_id": 123}
    assert 'X-Hub-Signature-256' in headers
    assert 'X-Webhook-Timestamp' in headers
    
    # Verify the signature
    timestamp = headers['X-Webhook-Timestamp']
    signature = headers['X-Hub-Signature-256'].replace('sha256=', '')
    
    assert verify_signature("mysecret", data, timestamp, signature) is True

def test_v2_signature_verification_replay_attack():
    secret = "mysecret"
    payload = json.dumps({"order_id": 123})
    
    # Generate signature with an old timestamp
    old_timestamp = str(int(time.time()) - 400) # 400 seconds ago, max age is 300
    old_signature = generate_signature(secret, payload, old_timestamp)
    
    assert verify_signature(secret, payload, old_timestamp, old_signature) is False
    
    # Valid recent timestamp
    recent_timestamp = str(int(time.time()) - 100)
    recent_signature = generate_signature(secret, payload, recent_timestamp)
    
    assert verify_signature(secret, payload, recent_timestamp, recent_signature) is True
    
    # Invalid signature
    assert verify_signature(secret, payload, recent_timestamp, "badsignature") is False

def test_v2_per_host_concurrency_limits():
    class DelayHttpClient(HttpClient):
        def __init__(self):
            self.concurrent_requests = {}
            self.max_observed = {}
            self.lock = threading.Lock()
            self.calls = 0

        def post(self, url: str, data: str, headers: dict) -> DeliveryResult:
            from urllib.parse import urlparse
            host = urlparse(url).hostname
            
            with self.lock:
                self.concurrent_requests[host] = self.concurrent_requests.get(host, 0) + 1
                if self.concurrent_requests[host] > self.max_observed.get(host, 0):
                    self.max_observed[host] = self.concurrent_requests[host]
            
            time.sleep(0.2)
            
            with self.lock:
                self.concurrent_requests[host] -= 1
                self.calls += 1
            return DeliveryResult(200, True)

    client = DelayHttpClient()
    
    host_limits = {
        "hosta.com": 5,
        "hostb.com": 2
    }
    
    dispatcher = WebhookDispatcher(client, num_workers=10, default_max_concurrent_per_host=1, host_limits=host_limits)
    
    dispatcher.add_subscriber(Subscriber("subA", "http://hosta.com/hook", "secret", "batch.*"))
    dispatcher.add_subscriber(Subscriber("subB", "http://hostb.com/hook", "secret", "batch.*"))
    dispatcher.add_subscriber(Subscriber("subC", "http://hostc.com/hook", "secret", "batch.*"))
    
    for i in range(10):
        dispatcher.publish(Event(f"batch.{i}", {"id": i}))
        
    time.sleep(3.0)
    dispatcher.stop()
    
    assert client.calls == 30 # 10 events * 3 subscribers
    assert client.max_observed["hosta.com"] <= 5
    assert client.max_observed["hostb.com"] <= 2
    assert client.max_observed["hostc.com"] <= 1
    
    assert client.max_observed["hostb.com"] == 2 # verify it actually hit 2

def test_v2_retry_backoff_and_dlq():
    client = MockHttpClient()
    client.fail_count = 10 # ensure all retries fail
    
    dispatcher = WebhookDispatcher(client, num_workers=2)
    sub = Subscriber("sub1", "http://example.com/fail", "secret", "user.*")
    dispatcher.add_subscriber(sub)
    
    dispatcher.publish(Event("user.created", {"user_id": 1}))
    
    time.sleep(2.0)
    dispatcher.stop()
    
    assert len(client.calls) == 4
    
    with dispatcher.dlq_lock:
        assert len(dispatcher.dlq) == 1
        dlq_task = dispatcher.dlq[0]
        assert dlq_task.event.topic == "user.created"
        assert dlq_task.attempt == 4

