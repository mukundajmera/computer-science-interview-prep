import hashlib
import hmac
import json
import logging
import random
import re
import threading
from typing import Any, Dict, List

from http_client import HttpClient, DeliveryResult

logger = logging.getLogger(__name__)

class Event:
    def __init__(self, topic: str, payload: Dict[str, Any]):
        self.topic = topic
        self.payload = payload

class Subscriber:
    def __init__(self, id: str, endpoint: str, secret: str, topic_regex: str):
        self.id = id
        self.endpoint = endpoint
        self.secret = secret
        self.topic_regex = re.compile(topic_regex)

class WebhookTask:
    def __init__(self, event: Event, subscriber: Subscriber):
        self.event = event
        self.subscriber = subscriber
        self.attempt = 0
        self.max_retries = 3
        self.base_delay_ms = 100

class WebhookDispatcher:
    def __init__(self, http_client: HttpClient, num_workers: int = 4, max_concurrent_per_dest: int = 5):
        self.http_client = http_client
        self.subscribers: Dict[str, Subscriber] = {}
        self.dlq: List[WebhookTask] = []
        self.dlq_lock = threading.Lock()
        
        self.queue: List[WebhookTask] = []
        self.queue_lock = threading.Lock()
        self.queue_cond = threading.Condition(self.queue_lock)
        
        self.max_concurrent_per_dest = max_concurrent_per_dest
        self.semaphores: Dict[str, threading.Semaphore] = {}
        self.sem_lock = threading.Lock()
        
        self.running = True
        self.workers = [threading.Thread(target=self._worker_loop, daemon=True) for _ in range(num_workers)]
        for w in self.workers:
            w.start()

    def add_subscriber(self, sub: Subscriber):
        self.subscribers[sub.id] = sub
        with self.sem_lock:
            if sub.endpoint not in self.semaphores:
                self.semaphores[sub.endpoint] = threading.Semaphore(self.max_concurrent_per_dest)

    def remove_subscriber(self, sub_id: str):
        if sub_id in self.subscribers:
            del self.subscribers[sub_id]

    def publish(self, event: Event):
        for sub in self.subscribers.values():
            if sub.topic_regex.match(event.topic):
                task = WebhookTask(event, sub)
                with self.queue_cond:
                    self.queue.append(task)
                    self.queue_cond.notify()

    def _get_semaphore(self, endpoint: str) -> threading.Semaphore:
        with self.sem_lock:
            if endpoint not in self.semaphores:
                self.semaphores[endpoint] = threading.Semaphore(self.max_concurrent_per_dest)
            return self.semaphores[endpoint]

    def _worker_loop(self):
        while self.running:
            task = None
            with self.queue_cond:
                while self.running and not self.queue:
                    self.queue_cond.wait()
                if not self.running:
                    break
                task = self.queue.pop(0)

            if task:
                self._process_task(task)

    def _process_task(self, task: WebhookTask):
        payload_str = json.dumps(task.event.payload)
        
        signature = hmac.new(
            task.subscriber.secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'Content-Type': 'application/json',
            'X-Hub-Signature-256': f'sha256={signature}'
        }

        sem = self._get_semaphore(task.subscriber.endpoint)
        
        success = False
        try:
            with sem:
                result = self.http_client.post(task.subscriber.endpoint, payload_str, headers)
                success = result.success
        except Exception as e:
            logger.error(f"Delivery failed: {e}")
            success = False

        if not success:
            task.attempt += 1
            if task.attempt <= task.max_retries:
                max_delay_ms = task.base_delay_ms * (2 ** task.attempt)
                delay_ms = random.uniform(0, max_delay_ms)
                
                # Use a timer to enqueue without blocking the worker
                timer = threading.Timer(delay_ms / 1000.0, self._requeue_task, args=[task])
                timer.daemon = True
                timer.start()
            else:
                with self.dlq_lock:
                    self.dlq.append(task)

    def _requeue_task(self, task: WebhookTask):
        if not self.running:
            return
        with self.queue_cond:
            self.queue.append(task)
            self.queue_cond.notify()

    def stop(self):
        self.running = False
        with self.queue_cond:
            self.queue_cond.notify_all()
        for w in self.workers:
            w.join(timeout=2.0)
