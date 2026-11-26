import uuid
from typing import List
from broker import MessageQueueBroker
from message import Message

class Consumer:
    def __init__(self, broker: MessageQueueBroker, group_id: str, topic_regex: str):
        self.id = str(uuid.uuid4())
        self.broker = broker
        self.group_id = group_id
        self.group = broker.get_or_create_consumer_group(group_id)
        self.topic_regex = topic_regex
        self.group.register_consumer(self.id)
        self._in_flight = {}

    def poll(self) -> List[Message]:
        messages = []
        topics = self.broker.get_topics_matching(self.topic_regex)
        assigned = self.group.get_assigned_partitions(self.id, topics)
        
        for topic, partition in assigned:
            result = self.group.read_message(topic, partition)
            if result:
                msg, offset = result
                self._in_flight[msg.id] = (topic.name, partition.id, offset)
                messages.append(msg)
        return messages

    def ack(self, message: Message):
        if message.id in self._in_flight:
            t_name, p_id, offset = self._in_flight.pop(message.id)
            self.group.ack(t_name, p_id, offset)

    def nack(self, message: Message):
        if message.id in self._in_flight:
            t_name, p_id, offset = self._in_flight.pop(message.id)
            self.group.nack(t_name, p_id, offset)

    def close(self):
        self.group.deregister_consumer(self.id)

    def poll_and_commit(self) -> List[Message]:
        messages = self.poll()
        for msg in messages:
            self.ack(msg)
        return messages
