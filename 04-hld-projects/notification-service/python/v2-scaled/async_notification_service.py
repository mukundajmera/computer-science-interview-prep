"""
Notification Service - V2 Scaled

Async notification service with priority queues.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List

import queue
import threading
import time
import hashlib


@dataclass
class NotificationMessage:
    """Message wrapper for queue."""
    notification: 'Notification'
    preferences: 'UserPreferences'
    enqueued_at: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    
    def increment_retry(self):
        self.retry_count += 1


class PriorityNotificationQueue:
    """Priority-based queue implementation."""
    
    def __init__(self):
        self._queue = queue.PriorityQueue()
    
    def enqueue(self, message: NotificationMessage):
        # Priority: Critical=0, High=1, Normal=2, Low=3
        priority_order = {
            'critical': 0,
            'high': 1,
            'normal': 2,
            'low': 3
        }
        priority = priority_order.get(
            message.notification.priority.value, 2)
        
        self._queue.put((priority, message.enqueued_at, message))
    
    def poll(self, timeout: float = 1.0) -> Optional[NotificationMessage]:
        try:
            _, _, message = self._queue.get(timeout=timeout)
            return message
        except queue.Empty:
            return None
    
    def size(self) -> int:
        return self._queue.qsize()


class DeadLetterQueue:
    """Dead letter queue for failed notifications."""
    
    def __init__(self):
        self._queue: List[NotificationMessage] = []
        self._lock = threading.Lock()
    
    def add(self, message: NotificationMessage):
        with self._lock:
            self._queue.append(message)
    
    def poll(self) -> Optional[NotificationMessage]:
        with self._lock:
            return self._queue.pop(0) if self._queue else None
    
    def size(self) -> int:
        return len(self._queue)


class AsyncNotificationService:
    """Async notification service with worker pool."""
    
    MAX_RETRY_COUNT = 6
    RETRY_DELAYS_SEC = [0, 60, 300, 900, 3600, 14400]
    
    def __init__(self, template_service, channel_router,
                 preference_service, repository, worker_count: int = 4):
        self._template_service = template_service
        self._renderer = TemplateRenderer()
        self._channel_router = channel_router
        self._preference_service = preference_service
        self._repository = repository
        self._main_queue = PriorityNotificationQueue()
        self._dlq = DeadLetterQueue()
        self._running = True
        self._workers: List[threading.Thread] = []
        
        # Start workers
        for i in range(worker_count):
            worker = threading.Thread(target=self._process_loop, daemon=True)
            worker.start()
            self._workers.append(worker)
    
    def send(self, request) -> dict:
        """Send notification asynchronously."""
        # Check user preferences
        prefs = self._preference_service.get_preferences(request.user_id)
        if not prefs.is_channel_enabled(request.channel):
            raise UserOptedOutError(
                f"User has disabled {request.channel.value} notifications")
        
        # Get and render template
        template = self._template_service.get_template(request.template_id)
        if not template:
            raise TemplateNotFoundError(request.template_id)
        
        content = self._renderer.render(template, request.variables)
        
        # Create notification
        notification = Notification.create(
            user_id=request.user_id,
            template_id=request.template_id,
            channel=request.channel,
            priority=request.priority,
            variables=request.variables,
            rendered_content=content.body
        )
        
        self._repository.save(notification)
        
        # Enqueue for async processing
        message = NotificationMessage(notification=notification, preferences=prefs)
        self._main_queue.enqueue(message)
        
        return {
            'notification_id': notification.notification_id,
            'status': notification.status.value,
            'estimated_delivery': self._estimate_delivery(request.priority)
        }
    
    def _process_loop(self):
        """Worker loop for processing notifications."""
        while self._running:
            try:
                message = self._main_queue.poll(timeout=1.0)
                if message:
                    self._process_message(message)
            except Exception as e:
                print(f"Worker error: {e}")
    
    def _process_message(self, message: NotificationMessage):
        """Process a single notification message."""
        notification = message.notification
        
        try:
            provider = self._channel_router.get_provider(notification.channel)
            result = provider.send(notification, message.preferences)
            
            if result.success:
                notification.mark_sent()
                notification.mark_delivered()
                self._repository.save(notification)
            else:
                self._handle_failure(message, result.error_message)
                
        except Exception as e:
            self._handle_failure(message, str(e))
    
    def _handle_failure(self, message: NotificationMessage, error: str):
        """Handle delivery failure with retry logic."""
        notification = message.notification
        notification.increment_attempt()
        
        if message.retry_count < self.MAX_RETRY_COUNT:
            message.increment_retry()
            delay = self.RETRY_DELAYS_SEC[message.retry_count]
            
            # Schedule retry
            def delayed_enqueue():
                time.sleep(delay)
                self._main_queue.enqueue(message)
            
            threading.Thread(target=delayed_enqueue, daemon=True).start()
            self._repository.save(notification)
        else:
            notification.mark_failed(error)
            self._repository.save(notification)
            self._dlq.add(message)
    
    def _estimate_delivery(self, priority) -> datetime:
        delay_seconds = {
            'critical': 1,
            'high': 30,
            'normal': 300,
            'low': 3600
        }.get(priority.value, 300)
        
        from datetime import timedelta
        return datetime.utcnow() + timedelta(seconds=delay_seconds)
    
    def get_status(self, notification_id: str):
        return self._repository.find_by_id(notification_id)
    
    def shutdown(self):
        self._running = False
        for worker in self._workers:
            worker.join(timeout=2.0)
    
    @property
    def queue_size(self) -> int:
        return self._main_queue.size()
    
    @property
    def dlq_size(self) -> int:
        return self._dlq.size()


class DeduplicationService:
    """Deduplication service to prevent duplicate notifications."""
    
    IDEMPOTENCY_TTL_SEC = 24 * 60 * 60  # 24 hours
    CONTENT_DEDUP_WINDOW_SEC = 60 * 60   # 1 hour
    
    def __init__(self):
        self._idempotency_store: Dict[str, str] = {}
        self._content_hashes: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def check_idempotency_key(self, key: Optional[str]) -> Optional[str]:
        """Check if notification with this key was already processed."""
        if not key:
            return None
        return self._idempotency_store.get(key)
    
    def store_idempotency_key(self, key: str, notification_id: str):
        """Store idempotency key after processing."""
        if key:
            self._idempotency_store[key] = notification_id
    
    def is_content_duplicate(self, user_id: str, template_id: str,
                            channel: str, variables: Dict) -> bool:
        """Check for content-based duplicate within time window."""
        hash_key = self._compute_content_hash(
            user_id, template_id, channel, variables)
        
        with self._lock:
            previous = self._content_hashes.get(hash_key)
            now = time.time()
            
            if previous and (now - previous) < self.CONTENT_DEDUP_WINDOW_SEC:
                return True
            
            self._content_hashes[hash_key] = now
            return False
    
    def _compute_content_hash(self, user_id: str, template_id: str,
                             channel: str, variables: Dict) -> str:
        content = f"{user_id}|{template_id}|{channel}|"
        if variables:
            sorted_vars = sorted(variables.items())
            content += ";".join(f"{k}={v}" for k, v in sorted_vars)
        
        return hashlib.sha256(content.encode()).hexdigest()
    
    def cleanup(self):
        """Clean up expired entries."""
        now = time.time()
        with self._lock:
            self._content_hashes = {
                k: v for k, v in self._content_hashes.items()
                if now - v < self.CONTENT_DEDUP_WINDOW_SEC
            }


class ProviderRateLimiter:
    """Rate limiter for providers."""
    
    def __init__(self):
        self._buckets: Dict[str, '_TokenBucket'] = {}
        self._lock = threading.Lock()
    
    def configure(self, provider_id: str, requests_per_second: int):
        self._buckets[provider_id] = _TokenBucket(
            capacity=requests_per_second,
            refill_rate=requests_per_second
        )
    
    def allow_request(self, provider_id: str) -> bool:
        bucket = self._buckets.get(provider_id)
        if not bucket:
            return True
        return bucket.try_consume()


class _TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self._lock = threading.Lock()
    
    def try_consume(self) -> bool:
        with self._lock:
            self._refill()
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, 
                         self.tokens + (elapsed * self.refill_rate))
        self.last_refill = now


# Import from v1 for type hints
from notification_service import (
    Notification, UserPreferences, TemplateRenderer
)


class TemplateNotFoundError(Exception):
    pass


class UserOptedOutError(Exception):
    pass
