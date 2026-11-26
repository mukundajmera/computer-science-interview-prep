import threading
from enum import Enum
from queue import Empty
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

    def submit_intent(self, event: str, recipient: str, channel: str, message: str, priority: int = 1) -> IntentState:
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
        self.dispatcher.enqueue(notification.Notification(recipient, f"{idempotency_key}|{message}", channel, priority))
        return IntentState.PENDING

    def dispatch(self, event: str, recipient: str, message: str, priority: int = 1):
        with self.lock:
            if recipient in self.unsubscribed_users:
                return
                
        channels = self.dispatcher.user_preferences.get_preferred_channels(recipient, event)
        for channel in channels:
            self.submit_intent(event, recipient, channel, message, priority)

    def process_callback(self, idempotency_key: str, success: bool):
        with self.lock:
            state = self.intents.get(idempotency_key)
            if state in (IntentState.COMPLETED, IntentState.FAILED):
                return
                
            self.intents[idempotency_key] = IntentState.COMPLETED if success else IntentState.FAILED

    def get_intent_state(self, idempotency_key: str) -> IntentState:
        with self.lock:
            return self.intents.get(idempotency_key)

    def wrap_channel(self, channel_type: str, original_channel):
        import notification
        service = self
        
        class WrappedChannel(notification.Channel):
            def send(self, notif):
                msg_parts = notif.message.split('|', 1)
                idempotency_key = msg_parts[0] if len(msg_parts) > 1 else notif.message
                
                with service.lock:
                    if service.intents.get(idempotency_key) == IntentState.PENDING:
                        service.intents[idempotency_key] = IntentState.IN_PROGRESS

                success = False
                try:
                    success = original_channel.send(notif)
                except Exception:
                    pass

                if success:
                    service.process_callback(idempotency_key, True)
                    with service.lock:
                        service.current_size -= 1
                else:
                    if notif.attempts >= service.max_retries:
                        service.process_callback(idempotency_key, False)
                        with service.lock:
                            service.current_size -= 1
                            
                return success

        self.dispatcher.channels[channel_type] = WrappedChannel()
