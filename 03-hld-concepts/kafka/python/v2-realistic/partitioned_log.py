import threading
import time

class Partition:
    def __init__(self, id):
        self.id = id
        self.log = []
        self.lock = threading.Lock()
        
    def append(self, message):
        with self.lock:
            offset = len(self.log)
            self.log.append(message)
            return offset
            
    def read(self, offset):
        with self.lock:
            if offset < len(self.log):
                return self.log[offset]
            return None

class Topic:
    def __init__(self, name, num_partitions=3):
        self.name = name
        self.partitions = [Partition(i) for i in range(num_partitions)]
        
    def produce(self, partition_id, message):
        return self.partitions[partition_id].append(message)
        
class ConsumerGroup:
    def __init__(self, topic, group_id, consumers=1):
        self.topic = topic
        self.group_id = group_id
        self.offsets = {i: 0 for i in range(len(topic.partitions))}
        self.lock = threading.Lock()
        
    def poll(self, partition_id):
        with self.lock:
            offset = self.offsets[partition_id]
            msg = self.topic.partitions[partition_id].read(offset)
            if msg is not None:
                self.offsets[partition_id] += 1
            return msg
