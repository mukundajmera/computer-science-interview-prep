
import time
from queue import PriorityQueue
import threading

class Notification:
    def __init__(self, user_id, message, channel_type, priority=1):
        self.user_id = user_id
        self.message = message
        self.channel_type = channel_type
        self.priority = priority
        self.timestamp = time.time()
        
    def __lt__(self, other):
        # Lower priority number = higher priority
        if self.priority == other.priority:
            return self.timestamp < other.timestamp
        return self.priority < other.priority

class Channel:
    def send(self, notification):
        pass

class EmailChannel(Channel):
    def send(self, notification):
        return True

class SMSChannel(Channel):
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
    def __init__(self, rate_limit=10, max_retries=None, **kwargs):
        self.channels = {
            "EMAIL": EmailChannel(),
            "SMS": SMSChannel()
        }
        self.queue = PriorityQueue()
        self.rate_limiter = RateLimiter(rate_limit)
        
    def enqueue(self, notification):
        self.queue.put(notification)
        
    def process_one(self):
        if not self.queue.empty():
            notification = self.queue.get()
            if self.rate_limiter.acquire(notification.channel_type):
                channel = self.channels.get(notification.channel_type)
                if channel:
                    channel.send(notification)
                    return True
            else:
                # Rate limit exceeded, normally we'd retry later
                # For v2, we just put it back (busy wait essentially, handled better in v3)
                self.queue.put(notification)
        return False
