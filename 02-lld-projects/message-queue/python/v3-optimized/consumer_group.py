import threading
from typing import Dict, Set, List, Tuple
from topic import Topic
from partition import Partition
from message import Message

class ConsumerGroup:
    def __init__(self, group_id: str):
        self.group_id = group_id
        self.consumers: Set[str] = set()
        self.lock = threading.RLock()
        
        # Topic -> Partition -> Offset
        self.read_offsets: Dict[str, Dict[int, int]] = {}
        self.unacked_messages: Dict[str, Dict[int, Set[int]]] = {}
        self.redelivery_offsets: Dict[str, Dict[int, Set[int]]] = {}
        self.committed_offsets: Dict[str, Dict[int, int]] = {}
        # Keep track of message instances mapping to offsets to assist DAG
        self.offset_to_message: Dict[str, Dict[int, Dict[int, Message]]] = {}

    def register_consumer(self, consumer_id: str):
        with self.lock:
            self.consumers.add(consumer_id)

    def deregister_consumer(self, consumer_id: str):
        with self.lock:
            if consumer_id in self.consumers:
                self.consumers.remove(consumer_id)

    def get_assigned_partitions(self, consumer_id: str, topics: List[Topic]) -> List[Tuple[Topic, Partition]]:
        with self.lock:
            consumers = sorted(list(self.consumers))
            if consumer_id not in consumers:
                return []
            idx = consumers.index(consumer_id)
            num_consumers = len(consumers)
            
            all_parts = []
            for t in sorted(topics, key=lambda x: x.name):
                for p in sorted(t.partitions, key=lambda x: x.id):
                    all_parts.append((t, p))
            
            assigned = []
            for i, part in enumerate(all_parts):
                if i % num_consumers == idx:
                    assigned.append(part)
            return assigned

    def read_message(self, topic: Topic, partition: Partition, dag=None) -> Tuple[Message, int]:
        with self.lock:
            t_name = topic.name
            p_id = partition.id
            
            for d in [self.read_offsets, self.unacked_messages, self.redelivery_offsets, self.committed_offsets, self.offset_to_message]:
                if t_name not in d:
                    d[t_name] = {}
                if p_id not in d[t_name]:
                    if d is self.unacked_messages or d is self.redelivery_offsets:
                        d[t_name][p_id] = set()
                    elif d is self.offset_to_message:
                        d[t_name][p_id] = {}
                    else:
                        d[t_name][p_id] = 0

            # Find next eligible message
            # Start with redelivery
            redeliveries = sorted(list(self.redelivery_offsets[t_name][p_id]))
            for offset in redeliveries:
                msg = self.offset_to_message[t_name][p_id].get(offset)
                if not msg:
                    msg = partition.read(offset)
                    if msg:
                        self.offset_to_message[t_name][p_id][offset] = msg
                
                if msg:
                    if not dag or dag.is_eligible(self.group_id, msg):
                        self.redelivery_offsets[t_name][p_id].remove(offset)
                        self.unacked_messages[t_name][p_id].add(offset)
                        return (msg, offset)
            
            # Read forward
            offset = self.read_offsets[t_name][p_id]
            while True:
                msg = partition.read(offset)
                if not msg:
                    break
                self.offset_to_message[t_name][p_id][offset] = msg
                
                if not dag or dag.is_eligible(self.group_id, msg):
                    self.unacked_messages[t_name][p_id].add(offset)
                    self.read_offsets[t_name][p_id] = offset + 1
                    return (msg, offset)
                else:
                    # Message not eligible yet, break to avoid consuming beyond DAG progress
                    break
            
            return None

    def ack(self, topic_name: str, partition_id: int, offset: int, dag=None):
        with self.lock:
            if topic_name in self.unacked_messages and partition_id in self.unacked_messages[topic_name]:
                self.unacked_messages[topic_name][partition_id].discard(offset)
                
                unacked = self.unacked_messages[topic_name][partition_id]
                read_off = self.read_offsets[topic_name][partition_id]
                if not unacked:
                    self.committed_offsets[topic_name][partition_id] = read_off
                else:
                    self.committed_offsets[topic_name][partition_id] = min(unacked)
                    
                if dag and topic_name in self.offset_to_message and partition_id in self.offset_to_message[topic_name]:
                    msg = self.offset_to_message[topic_name][partition_id].get(offset)
                    if msg:
                        dag.record_ack(self.group_id, msg)
                        # Optionally clear from memory if all dependencies met?

    def nack(self, topic_name: str, partition_id: int, offset: int):
        with self.lock:
            if topic_name in self.unacked_messages and partition_id in self.unacked_messages[topic_name]:
                if offset in self.unacked_messages[topic_name][partition_id]:
                    self.unacked_messages[topic_name][partition_id].remove(offset)
                    self.redelivery_offsets[topic_name][partition_id].add(offset)
