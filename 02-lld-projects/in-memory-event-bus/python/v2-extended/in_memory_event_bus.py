import threading
import queue
from typing import Dict, List, Any, Callable, Optional

class Partition:
    def __init__(self, id: int):
        self.id = id
        self.events: List[Any] = []
        self.lock = threading.Lock()
        
    def append(self, event: Any) -> int:
        with self.lock:
            self.events.append(event)
            return len(self.events) - 1
            
    def read(self, offset: int) -> Optional[Any]:
        with self.lock:
            if offset < len(self.events):
                return self.events[offset]
            return None

class Topic:
    def __init__(self, name: str, num_partitions: int):
        self.name = name
        self.partitions = [Partition(i) for i in range(num_partitions)]
        
    def publish(self, event: Any, partition_key: int) -> int:
        idx = abs(partition_key) % len(self.partitions)
        return self.partitions[idx].append(event)

class Subscriber:
    def __init__(self, handler: Callable[[Any], None], capacity: int, policy: str):
        self.handler = handler
        self.queue = queue.Queue(maxsize=capacity)
        self.policy = policy
        self.active = True
        self.worker = threading.Thread(target=self._run)
        self.worker.start()
        
    def _run(self):
        while self.active or not self.queue.empty():
            try:
                event = self.queue.get(timeout=0.1)
                try:
                    self.handler(event)
                except Exception:
                    pass
                self.queue.task_done()
            except queue.Empty:
                continue

    def push(self, event: Any):
        if not self.active:
            return
        if self.policy == "BLOCK":
            self.queue.put(event)
        elif self.policy == "DROP":
            try:
                self.queue.put_nowait(event)
            except queue.Full:
                pass
        elif self.policy == "REJECT":
            try:
                self.queue.put_nowait(event)
            except queue.Full:
                raise RuntimeError("Queue is full")

    def shutdown(self):
        self.active = False
        self.worker.join(timeout=2.0)

class InMemoryEventBus:
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.offsets: Dict[str, Dict[str, Dict[int, int]]] = {}
        self.subscribers: Dict[str, List[Subscriber]] = {}
        self.lock = threading.Lock()

    def create_topic(self, name: str, num_partitions: int = 1):
        with self.lock:
            if name not in self.topics:
                self.topics[name] = Topic(name, num_partitions)
                self.subscribers[name] = []

    def publish(self, topic_name: str, event: Any, partition_key: int = 0):
        with self.lock:
            if topic_name not in self.topics:
                self.topics[topic_name] = Topic(topic_name, 1)
                self.subscribers[topic_name] = []
            topic = self.topics[topic_name]
            subs = list(self.subscribers[topic_name])
            
        topic.publish(event, partition_key)
        for sub in subs:
            sub.push(event)

    def subscribe(self, *args):
        if len(args) == 4:
            topic_name, handler, capacity, policy = args
            with self.lock:
                if topic_name not in self.subscribers:
                    self.subscribers[topic_name] = []
                self.subscribers[topic_name].append(Subscriber(handler, capacity, policy))
        elif len(args) == 2:
            group, topic_name = args
            with self.lock:
                if group not in self.offsets:
                    self.offsets[group] = {}
                if topic_name not in self.offsets[group]:
                    self.offsets[group][topic_name] = {}
                    
                topic = self.topics.get(topic_name)
                if topic:
                    for p in topic.partitions:
                        if p.id not in self.offsets[group][topic_name]:
                            self.offsets[group][topic_name][p.id] = 0
        else:
            raise ValueError("Invalid arguments for subscribe")
            
    def unsubscribe_all(self):
        with self.lock:
            subs_to_shutdown = []
            for subs in self.subscribers.values():
                for sub in subs:
                    subs_to_shutdown.append(sub)
            self.subscribers.clear()
            
        for sub in subs_to_shutdown:
            sub.shutdown()

    def poll(self, group: str, topic_name: str, partition_id: int) -> Optional[Any]:
        with self.lock:
            if group not in self.offsets or topic_name not in self.offsets[group]:
                return None
            topic = self.topics.get(topic_name)
            if not topic:
                return None
                
            offset = self.offsets[group][topic_name].get(partition_id, 0)
        return topic.partitions[partition_id].read(offset)

    def commit_offset(self, group: str, topic_name: str, partition_id: int, offset: int):
        with self.lock:
            if group in self.offsets and topic_name in self.offsets[group]:
                curr = self.offsets[group][topic_name].get(partition_id, 0)
                self.offsets[group][topic_name][partition_id] = max(curr, offset)
