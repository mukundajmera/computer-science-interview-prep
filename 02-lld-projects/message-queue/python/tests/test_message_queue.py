import pytest
import os
import sys

# Make sure v1-basic is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from broker import MessageQueueBroker
from producer import Producer
from consumer import Consumer
from message import Message
from subscriber_dag import SubscriberDAG
from retry_policy import RetryPolicy

class TestMessageQueue:
    def setup_method(self):
        self.broker = MessageQueueBroker()
        self.broker.create_topic("test_topic", 3)

    def test_multi_partition_publish_subscribe(self):
        producer = Producer(self.broker)
        producer.send("test_topic", Message("1", "Msg1"))
        producer.send("test_topic", Message("2", "Msg2"))
        producer.send("test_topic", Message("3", "Msg3"))

        consumer = Consumer(self.broker, "group1", "test_topic")
        polled = consumer.poll_and_commit()
        assert len(polled) == 3

        topic = self.broker.get_topic("test_topic")
        assert topic.partitions[0].size() == 1
        assert topic.partitions[1].size() == 1
        assert topic.partitions[2].size() == 1

    def test_consumer_group_offset_independence(self):
        producer = Producer(self.broker)
        producer.send("test_topic", Message("1", "Msg1"))

        consumer_g1 = Consumer(self.broker, "group1", "test_topic")
        consumer_g2 = Consumer(self.broker, "group2", "test_topic")

        polled_g1 = consumer_g1.poll_and_commit()
        assert len(polled_g1) == 1

        polled_g2 = consumer_g2.poll_and_commit()
        assert len(polled_g2) == 1

        polled_g1_again = consumer_g1.poll_and_commit()
        assert len(polled_g1_again) == 0

    def test_subscriber_dag_execution_order(self):
        dag = SubscriberDAG()
        execution_order = []

        dag.add_subscriber("A", lambda: execution_order.append("A"))
        dag.add_subscriber("B", lambda: execution_order.append("B"))
        dag.add_subscriber("C", lambda: execution_order.append("C"))

        dag.add_dependency("A", "B")
        dag.add_dependency("B", "C")

        dag.execute()

        assert execution_order == ["A", "B", "C"]

    def test_retry_and_dlq_behavior(self):
        policy = RetryPolicy(max_retries=2, backoff_millis=10)
        bad_message = Message("error", "Bad payload")

        def failing_action():
            raise Exception("Simulated failure")

        success = policy.execute(failing_action, bad_message)

        assert not success
        assert len(policy.dead_letter_queue) == 1
        assert policy.dead_letter_queue[0] == bad_message
