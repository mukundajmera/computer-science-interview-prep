import time
from queue import PriorityQueue, Empty
import threading
import math

class Notification:
    def __init__(self, user_id, message, channel_type, priority=1):
        self.user_id = user_id
        self.message = message
        self.channel_type = channel_type
        self.priority = priority
        self.timestamp = time.time()
        self.attempts = 0
        self.next_retry_time = 0
        
    def __lt__(self, other):
        if self.priority == other.priority:
            return self.timestamp < other.timestamp
        return self.priority < other.priority

class UserPreferenceMatrix:
    def __init__(self):
        self.preferences = {}
        
    def set_preference(self, user_id, notification_type, channels):
        if user_id not in self.preferences:
            self.preferences[user_id] = {}
        self.preferences[user_id][notification_type] = channels
        
    def get_preferred_channels(self, user_id, notification_type):
        return self.preferences.get(user_id, {}).get(notification_type, ["EMAIL"])

class Channel:
    def send(self, notification):
        pass

class EmailChannel(Channel):
    def send(self, notification):
        return notification.user_id != "fail_first"

class SMSChannel(Channel):
    def send(self, notification):
        return True

class PushChannel(Channel):
    def send(self, notification):
        return True

class SlackChannel(Channel):
    def send(self, notification):
        return True

class RateLimiter:
    def __init__(self, limit):
        self.limit = limit
        self.counts = {}
        self.lock = threading.Lock()
        
    def acquire(self, channel_type):
        with self.lock:
            count = self.counts.get(channel_type, 0)
            if count < self.limit:
                self.counts[channel_type] = count + 1
                return True
            return False

class Dispatcher:
    def __init__(self, rate_limit=10, max_retries=3):
        self.channels = {
            "EMAIL": EmailChannel(),
            "SMS": SMSChannel(),
            "PUSH": PushChannel(),
            "SLACK": SlackChannel()
        }
        self.queue = PriorityQueue()
        self.retry_queue = PriorityQueue()
        self.rate_limiter = RateLimiter(rate_limit)
        self.user_preferences = UserPreferenceMatrix()
        self.max_retries = max_retries
        self.lock = threading.Lock()
        
    def dispatch_based_on_preference(self, user_id, message, notification_type, priority=1):
        channels = self.user_preferences.get_preferred_channels(user_id, notification_type)
        enqueued = False
        for channel in channels:
            n = Notification(user_id, message, channel, priority)
            self.enqueue(n)
            enqueued = True
        return enqueued
        
    def enqueue(self, notification):
        self.queue.put(notification)
        
    def _handle_retry(self, notification):
        notification.attempts += 1
        if notification.attempts <= self.max_retries:
            # Exponential backoff: base * 2^attempts
            delay = 1.0 * (2 ** notification.attempts)
            notification.next_retry_time = time.time() + delay
            self.retry_queue.put((notification.next_retry_time, notification))
            
    def process_one(self):
        now = time.time()
        
        with self.lock:
            # Move ripe retry items to main queue
            while not self.retry_queue.empty():
                retry_time, notif = self.retry_queue.queue[0]
                if retry_time <= now:
                    self.retry_queue.get()
                    self.queue.put(notif)
                else:
                    break
                    
            try:
                notification = self.queue.get_nowait()
            except Empty:
                return False
                
            channel = self.channels.get(notification.channel_type)
            if not channel:
                return False
                
            if self.rate_limiter.acquire(notification.channel_type):
                success = channel.send(notification)
                if not success:
                    self._handle_retry(notification)
                return success
            else:
                # Rate limited, essentially a temporary failure
                self._handle_retry(notification)
                return False
