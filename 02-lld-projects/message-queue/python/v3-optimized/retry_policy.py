import time
import math
from typing import Callable, List
from message import Message

class RetryPolicy:
    def __init__(self, max_retries: int, initial_backoff_millis: int, max_backoff_millis: int = None, multiplier: float = 2.0):
        self.max_retries = max_retries
        self.initial_backoff_millis = initial_backoff_millis
        self.max_backoff_millis = max_backoff_millis or (initial_backoff_millis * 10)
        self.multiplier = multiplier
        self.dead_letter_queue: List[Message] = []

    def execute(self, action: Callable, message: Message) -> bool:
        attempts = 0
        while attempts <= self.max_retries:
            try:
                action()
                return True
            except Exception:
                attempts += 1
                if attempts <= self.max_retries:
                    backoff = min(self.initial_backoff_millis * math.pow(self.multiplier, attempts - 1), self.max_backoff_millis)
                    time.sleep(backoff / 1000.0)
                    
        self.dead_letter_queue.append(message)
        return False
