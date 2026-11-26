import threading
from typing import List, Optional
from message import Message

class Partition:
    def __init__(self, partition_id: int):
        self.id = partition_id
        self.messages: List[Message] = []
        self.lock = threading.RLock()

    def append(self, message: Message):
        with self.lock:
            self.messages.append(message)

    def read(self, offset: int) -> Optional[Message]:
        with self.lock:
            if 0 <= offset < len(self.messages):
                return self.messages[offset]
            return None

    def size(self) -> int:
        with self.lock:
            return len(self.messages)
