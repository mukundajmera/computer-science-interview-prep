from broker import MessageQueueBroker
from message import Message

class Producer:
    def __init__(self, broker: MessageQueueBroker):
        self.broker = broker

    def send(self, topic: str, message: Message):
        self.broker.publish(topic, message)
