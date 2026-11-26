import pytest
import time
import sys
import os
import importlib

# Clean sys modules to allow reloading since test_message_queue.py loads v1-basic
import sys
modules_to_remove = [m for m in sys.modules if m in ['broker', 'producer', 'consumer', 'message', 'subscriber_dag', 'retry_policy', 'consumer_group', 'topic', 'partition']]
for m in modules_to_remove:
    del sys.modules[m]

# Add v3 optimized at the front
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

from broker import MessageQueueBroker
from producer import Producer
from consumer import Consumer
from message import Message
from retry_policy import RetryPolicy

def test_consumer_group_offsets():
    broker = MessageQueueBroker()
    broker.create_topic("topic1", 1)
    producer = Producer(broker)
    
    producer.send("topic1", Message("m1", "payload1"))
    producer.send("topic1", Message("m2", "payload2"))
    
    c1 = Consumer(broker, "group1", "topic1")
    
    # First poll should get m1
    msgs = c1.poll()
    assert len(msgs) == 1
    assert msgs[0].id == "m1"
    
    # Not acked yet, second poll gets m2
    msgs = c1.poll()
    assert len(msgs) == 1
    assert msgs[0].id == "m2"
    
    c1.ack(Message("m2", "payload2")) # Ack m2
    c1.nack(Message("m1", "payload1")) # Nack m1 explicitly to trigger redelivery
    
    msgs = c1.poll()
    assert len(msgs) == 1
    assert msgs[0].id == "m1"
    
    c1.ack(msgs[0])
    
    # Now all read
    assert len(c1.poll()) == 0

def test_subscriber_dag_dependencies():
    broker = MessageQueueBroker()
    broker.create_topic("topic2", 1)
    
    dag = broker.get_dag("topic2")
    dag.add_dependency("groupA", "groupB") # groupB depends on groupA
    
    producer = Producer(broker)
    producer.send("topic2", Message("m1", "data"))
    
    cA = Consumer(broker, "groupA", "topic2")
    cB = Consumer(broker, "groupB", "topic2")
    
    # cB polls, but cannot read because cA hasn't acked
    msgs_B = cB.poll()
    assert len(msgs_B) == 0
    
    # cA polls and gets the message
    msgs_A = cA.poll()
    assert len(msgs_A) == 1
    assert msgs_A[0].id == "m1"
    
    # Still cB cannot read
    msgs_B = cB.poll()
    assert len(msgs_B) == 0
    
    # cA acks
    cA.ack(msgs_A[0])
    
    # Now cB can read
    msgs_B = cB.poll()
    assert len(msgs_B) == 1
    assert msgs_B[0].id == "m1"

def test_dlq_retry_policy():
    policy = RetryPolicy(max_retries=2, initial_backoff_millis=10)
    
    fail_count = 0
    def failing_action():
        nonlocal fail_count
        fail_count += 1
        raise ValueError("error")
        
    msg = Message("m1", "test")
    success = policy.execute(failing_action, msg)
    
    assert not success
    assert fail_count == 3 # 1 initial + 2 retries
    assert len(policy.dead_letter_queue) == 1
    assert policy.dead_letter_queue[0].id == "m1"

def test_load_balancing():
    broker = MessageQueueBroker()
    broker.create_topic("topic3", 2)
    
    c1 = Consumer(broker, "group1", "topic3")
    c2 = Consumer(broker, "group1", "topic3")
    
    topics = broker.get_topics_matching("topic3")
    assert len(c1.group.get_assigned_partitions(c1.id, topics)) == 1
    assert len(c2.group.get_assigned_partitions(c2.id, topics)) == 1

def test_regex_subscription():
    broker = MessageQueueBroker()
    broker.create_topic("test_a", 1)
    broker.create_topic("test_b", 1)
    
    producer = Producer(broker)
    producer.send("test_a", Message("m1", "a"))
    producer.send("test_b", Message("m2", "b"))
    
    c = Consumer(broker, "group1", "test_.*")
    
    msgs = c.poll()
    assert len(msgs) == 2
    ids = {m.id for m in msgs}
    assert "m1" in ids
    assert "m2" in ids
