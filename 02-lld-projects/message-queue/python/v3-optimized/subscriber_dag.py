from typing import Dict, List, Callable, Set
from message import Message
import threading

class SubscriberDAG:
    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        self.dependencies: Dict[str, Set[str]] = {} # node -> depends_on
        self.reverse_dependencies: Dict[str, Set[str]] = {} # node -> blocking
        self.lock = threading.RLock()
        
        # Message ID -> (Subscriber Group -> Boolean ACK)
        self.message_acks: Dict[str, Dict[str, bool]] = {}

    def add_dependency(self, parent_group: str, child_group: str):
        with self.lock:
            if child_group not in self.dependencies:
                self.dependencies[child_group] = set()
            self.dependencies[child_group].add(parent_group)
            
            if parent_group not in self.reverse_dependencies:
                self.reverse_dependencies[parent_group] = set()
            self.reverse_dependencies[parent_group].add(child_group)

    def is_eligible(self, group_id: str, message: Message) -> bool:
        with self.lock:
            if group_id not in self.dependencies or not self.dependencies[group_id]:
                return True
            
            msg_id = message.id
            if msg_id not in self.message_acks:
                return False
                
            for dep in self.dependencies[group_id]:
                if not self.message_acks[msg_id].get(dep, False):
                    return False
            return True

    def record_ack(self, group_id: str, message: Message):
        with self.lock:
            msg_id = message.id
            if msg_id not in self.message_acks:
                self.message_acks[msg_id] = {}
            self.message_acks[msg_id][group_id] = True
