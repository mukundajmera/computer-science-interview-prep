import time
from typing import Callable, List
from message import Message

class RetryPolicy:
    def __init__(self, max_retries: int, backoff_millis: int):
        self.max_retries = max_retries
        self.backoff_millis = backoff_millis
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
                    time.sleep(self.backoff_millis / 1000.0)
                    
        self.dead_letter_queue.append(message)
        return False
