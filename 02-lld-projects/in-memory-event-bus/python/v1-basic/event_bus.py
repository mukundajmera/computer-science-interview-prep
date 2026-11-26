
import threading
from typing import Dict, List, Any

class EventBus:
    def __init__(self):
        self.topics: Dict[str, List[Any]] = {}
        self.lock = threading.Lock()
        self.subscribers: Dict[str, List[Any]] = {}

    def create_topic(self, topic: str):
        with self.lock:
            if topic not in self.topics:
                self.topics[topic] = []
                self.subscribers[topic] = []

    def publish(self, topic: str, event: Any):
        with self.lock:
            if topic not in self.topics:
                self.topics[topic] = []
                self.subscribers[topic] = []
            self.topics[topic].append(event)
            for sub in self.subscribers[topic]:
                sub(event)

    def subscribe(self, topic: str, callback):
        with self.lock:
            if topic not in self.topics:
                self.topics[topic] = []
                self.subscribers[topic] = []
            self.subscribers[topic].append(callback)
