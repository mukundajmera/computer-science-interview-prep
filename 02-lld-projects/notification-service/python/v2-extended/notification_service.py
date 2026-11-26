import threading
from enum import Enum
from typing import Dict, Set
import sys

class IntentState(Enum):
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    FAILED = 4
    CONFLICT = 5

class NotificationService:
    def __init__(self, dispatcher, capacity: int, max_retries: int):
        self.dispatcher = dispatcher
        self.capacity = capacity
        self.max_retries = max_retries
        self.intents: Dict[str, IntentState] = {}
        self.current_size = 0
        self.unsubscribed_users: Set[str] = set()
        self.lock = threading.Lock()

    def unsubscribe(self, user_id: str):
        with self.lock:
            self.unsubscribed_users.add(user_id)

    def generate_idempotency_key(self, event: str, recipient: str, channel: str) -> str:
        return f"{event}:{recipient}:{channel}"

    def submit_intent(self, event: str, recipient: str, channel: str, message: str) -> IntentState:
        with self.lock:
            if recipient in self.unsubscribed_users:
                return IntentState.FAILED

            idempotency_key = self.generate_idempotency_key(event, recipient, channel)

            if idempotency_key in self.intents:
                return IntentState.CONFLICT

            if self.current_size >= self.capacity:
                self.intents[idempotency_key] = IntentState.FAILED
                return IntentState.FAILED

            self.intents[idempotency_key] = IntentState.PENDING
            self.current_size += 1
            
        import notification
        # Background processing to avoid blocking main thread on hangs
        notification_obj = notification.Notification(recipient, f"{idempotency_key}|{message}", channel)
        thread = threading.Thread(target=self._process_intent, args=(idempotency_key, notification_obj))
        thread.daemon = True
        thread.start()
        
        return IntentState.PENDING

    def _process_intent(self, idempotency_key: str, notification):
        with self.lock:
            self.intents[idempotency_key] = IntentState.IN_PROGRESS
            
        attempts = 0
        success = False
        while attempts <= self.max_retries and not success:
            attempts += 1
            try:
                channel = self.dispatcher.channels.get(notification.channel_type)
                if channel:
                    success = channel.send(notification)
            except Exception:
                success = False
                
        with self.lock:
            self.current_size -= 1
            if success:
                self.intents[idempotency_key] = IntentState.COMPLETED
            else:
                self.intents[idempotency_key] = IntentState.FAILED

    def get_intent_state(self, idempotency_key: str) -> IntentState:
        with self.lock:
            return self.intents.get(idempotency_key)

    def wrap_channel(self, channel_type: str, original_channel):
        self.dispatcher.channels[channel_type] = original_channel
