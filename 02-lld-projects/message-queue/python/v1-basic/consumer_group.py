import threading
from typing import Dict

class ConsumerGroup:
    def __init__(self, group_id: str):
        self.group_id = group_id
        # Topic -> Partition -> Offset
        self.offsets: Dict[str, Dict[int, int]] = {}
        self.lock = threading.Lock()

    def get_offset(self, topic_name: str, partition_id: int) -> int:
        with self.lock:
            if topic_name not in self.offsets:
                self.offsets[topic_name] = {}
            if partition_id not in self.offsets[topic_name]:
                self.offsets[topic_name][partition_id] = 0
            return self.offsets[topic_name][partition_id]

    def commit_offset(self, topic_name: str, partition_id: int, new_offset: int):
        with self.lock:
            if topic_name not in self.offsets:
                self.offsets[topic_name] = {}
            current_offset = self.offsets[topic_name].get(partition_id, 0)
            if new_offset > current_offset:
                self.offsets[topic_name][partition_id] = new_offset
