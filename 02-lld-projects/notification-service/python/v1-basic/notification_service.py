import threading
from enum import Enum
from notification import Notification

class IntentState(Enum):
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    CONFLICT = 4
    FAILED = 5

class NotificationService:
    def __init__(self, dispatcher, capacity, max_retries):
        self.dispatcher = dispatcher
        self.capacity = capacity
        self.max_retries = max_retries
        self.intent_states = {}
        self.unsubscribed_users = set()
        self.queue_size = 0
        self.lock = threading.Lock()

    def unsubscribe(self, user_id):
        with self.lock:
            self.unsubscribed_users.add(user_id)
            
    def wrap_channel(self, channel_type, channel):
        self.dispatcher.channels[channel_type] = channel

    def submit_intent(self, event, user_id, channel_type, message):
        with self.lock:
            if user_id in self.unsubscribed_users:
                return IntentState.FAILED
                
            idempotency_key = f"{event}:{user_id}:{channel_type}"
            if idempotency_key in self.intent_states:
                return IntentState.CONFLICT
                
            if self.queue_size >= self.capacity:
                self.intent_states[idempotency_key] = IntentState.FAILED
                return IntentState.FAILED
                
            self.intent_states[idempotency_key] = IntentState.PENDING
            self.queue_size += 1
            
        notification = Notification(user_id, message, channel_type)
        thread = threading.Thread(target=self._process_intent, args=(idempotency_key, notification))
        thread.daemon = True
        thread.start()
        
        return IntentState.PENDING

    def _process_intent(self, idempotency_key, notification):
        with self.lock:
            self.intent_states[idempotency_key] = IntentState.IN_PROGRESS
            
        attempts = 0
        success = False
        while attempts <= self.max_retries and not success:
            attempts += 1
            try:
                success = self.dispatcher.dispatch(notification)
            except Exception:
                success = False
                
        with self.lock:
            self.queue_size -= 1
            if success:
                self.intent_states[idempotency_key] = IntentState.COMPLETED
            else:
                self.intent_states[idempotency_key] = IntentState.FAILED

    def get_intent_state(self, idempotency_key):
        with self.lock:
            return self.intent_states.get(idempotency_key)
