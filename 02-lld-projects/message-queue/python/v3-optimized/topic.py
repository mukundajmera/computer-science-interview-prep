from typing import List
from partition import Partition
from message import Message
import threading

class Topic:
    def __init__(self, name: str, num_partitions: int):
        self.name = name
        self.partitions = [Partition(i) for i in range(num_partitions)]
        self.round_robin_counter = 0
        self.counter_lock = threading.Lock()

    def publish(self, message: Message):
        with self.counter_lock:
            partition_index = self.round_robin_counter % len(self.partitions)
            self.round_robin_counter += 1
        self.partitions[partition_index].append(message)
