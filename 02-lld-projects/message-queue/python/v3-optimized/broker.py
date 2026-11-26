from typing import Dict, List
import re
from topic import Topic
from consumer_group import ConsumerGroup
from message import Message
from subscriber_dag import SubscriberDAG
import threading

class MessageQueueBroker:
    def __init__(self):
        self.topics: Dict[str, Topic] = {}
        self.consumer_groups: Dict[str, ConsumerGroup] = {}
        self.dags: Dict[str, SubscriberDAG] = {}
        self.lock = threading.Lock()

    def create_topic(self, name: str, partitions: int):
        with self.lock:
            if name not in self.topics:
                self.topics[name] = Topic(name, partitions)
                self.dags[name] = SubscriberDAG(name)

    def get_topic(self, name: str) -> Topic:
        with self.lock:
            return self.topics.get(name)

    def get_topics_matching(self, regex: str) -> List[Topic]:
        matched = []
        pattern = re.compile(regex)
        with self.lock:
            for topic_name, topic in self.topics.items():
                if pattern.match(topic_name):
                    matched.append(topic)
        return matched

    def publish(self, topic_name: str, message: Message):
        with self.lock:
            topic = self.topics.get(topic_name)
        if topic:
            topic.publish(message)
        else:
            raise ValueError(f"Topic does not exist: {topic_name}")

    def get_or_create_consumer_group(self, group_id: str) -> ConsumerGroup:
        with self.lock:
            if group_id not in self.consumer_groups:
                self.consumer_groups[group_id] = ConsumerGroup(group_id)
            return self.consumer_groups[group_id]
            
    def get_dag(self, topic_name: str) -> SubscriberDAG:
        with self.lock:
            return self.dags.get(topic_name)
