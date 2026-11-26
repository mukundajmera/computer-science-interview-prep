from typing import List
from broker import MessageQueueBroker
from message import Message

class Consumer:
    def __init__(self, broker: MessageQueueBroker, group_id: str, topic_regex: str):
        self.broker = broker
        self.group = broker.get_or_create_consumer_group(group_id)
        self.topic_regex = topic_regex

    def poll(self) -> List[Message]:
        messages = []
        topics = self.broker.get_topics_matching(self.topic_regex)
        for topic in topics:
            for partition in topic.partitions:
                offset = self.group.get_offset(topic.name, partition.id)
                msg = partition.read(offset)
                if msg:
                    messages.append(msg)
        return messages

    def poll_and_commit(self) -> List[Message]:
        messages = []
        topics = self.broker.get_topics_matching(self.topic_regex)
        for topic in topics:
            for partition in topic.partitions:
                offset = self.group.get_offset(topic.name, partition.id)
                msg = partition.read(offset)
                if msg:
                    messages.append(msg)
                    self.group.commit_offset(topic.name, partition.id, offset + 1)
        return messages

    def commit(self, topic_name: str, partition_id: int, new_offset: int):
        self.group.commit_offset(topic_name, partition_id, new_offset)
