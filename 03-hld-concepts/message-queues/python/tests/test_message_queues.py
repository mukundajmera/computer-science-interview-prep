import unittest
import sys
import os
import time
import tempfile
import shutil
import threading

# Dynamically adjust path to allow importing from hyphenated directories
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-realistic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-production'))

from simple_queue import SimpleQueue
from pubsub_queue import PubSubQueue
from durable_queue import DurableQueue, IdempotentConsumerWrapper

class TestSimpleQueue(unittest.TestCase):
    def test_enqueue_dequeue(self):
        q = SimpleQueue[int](max_size=5)
        self.assertTrue(q.is_empty())
        self.assertTrue(q.enqueue(1))
        self.assertTrue(q.enqueue(2))
        self.assertFalse(q.is_empty())
        self.assertEqual(q.size(), 2)
        
        self.assertEqual(q.dequeue(), 1)
        self.assertEqual(q.dequeue(), 2)
        self.assertTrue(q.is_empty())

    def test_full_backpressure(self):
        q = SimpleQueue[int](max_size=2)
        self.assertTrue(q.enqueue(1))
        self.assertTrue(q.enqueue(2))
        self.assertTrue(q.is_full())
        
        # Enqueue with small timeout should fail
        self.assertFalse(q.enqueue(3, timeout=0.01))
        
        # Dequeue to make space
        self.assertEqual(q.dequeue(), 1)
        self.assertFalse(q.is_full())
        
        # Now it should work
        self.assertTrue(q.enqueue(3, timeout=0.01))

    def test_empty_timeout(self):
        q = SimpleQueue[int](max_size=2)
        # Dequeue from empty queue with timeout should return None
        self.assertIsNone(q.dequeue(timeout=0.01))

    def test_clear(self):
        q = SimpleQueue[int](max_size=5)
        q.enqueue(1)
        q.enqueue(2)
        q.clear()
        self.assertTrue(q.is_empty())


class TestPubSubQueue(unittest.TestCase):
    def test_publish_and_pull(self):
        q = PubSubQueue[str]()
        q.create_topic("alerts")
        q.subscribe("alerts", "group1")
        
        published = q.publish("alerts", "CPU High")
        self.assertEqual(published, 1)
        
        msg = q.pull("alerts", "group1")
        self.assertIsNotNone(msg)
        self.assertEqual(msg.payload, "CPU High")
        
        # Successfully process and ack
        self.assertTrue(q.ack("alerts", "group1", msg.id))
        
        # Another pull should return nothing
        self.assertIsNone(q.pull("alerts", "group1"))

    def test_multiple_consumer_groups(self):
        q = PubSubQueue[int]()
        q.subscribe("metrics", "cg_dashboard")
        q.subscribe("metrics", "cg_archive")
        
        q.publish("metrics", 42)
        
        # Both groups should get a copy
        m1 = q.pull("metrics", "cg_dashboard")
        m2 = q.pull("metrics", "cg_archive")
        
        self.assertIsNotNone(m1)
        self.assertIsNotNone(m2)
        self.assertEqual(m1.payload, 42)
        self.assertEqual(m2.payload, 42)
        self.assertNotEqual(m1.id, m2.id)

    def test_visibility_timeout_and_redelivery(self):
        q = PubSubQueue[str]()
        # Very short visibility timeout
        q.subscribe("logs", "group1", visibility_timeout_sec=0.1)
        q.publish("logs", "error")
        
        msg1 = q.pull("logs", "group1")
        self.assertIsNotNone(msg1)
        
        # Immediate pull should return nothing because msg1 is in-flight
        self.assertIsNone(q.pull("logs", "group1"))
        
        # Wait for visibility timeout to expire
        time.sleep(0.15)
        
        # Now pull should return the redelivered message
        msg2 = q.pull("logs", "group1")
        self.assertIsNotNone(msg2)
        self.assertEqual(msg1.payload, msg2.payload)
        self.assertEqual(msg1.id, msg2.id)
        
        q.ack("logs", "group1", msg2.id)

    def test_dead_letter_queue(self):
        q = PubSubQueue[str]()
        # Short timeout to easily trigger redeliveries
        q.subscribe("task", "worker", visibility_timeout_sec=0.1)
        
        # Need to hack into the internal group to override max deliveries for fast test
        group = q._topics["task"]["worker"]
        group._max_deliveries = 2
        
        q.publish("task", "fail_job")
        
        # Delivery 1 (delivery_count becomes 1)
        msg1 = q.pull("task", "worker")
        self.assertIsNotNone(msg1)
        
        # Wait to expire
        time.sleep(0.15)
        
        # Delivery 2 (delivery_count becomes 2, which == max_deliveries, so it goes to DLQ!)
        # The pull() logic returns None when it puts something in the DLQ.
        msg2 = q.pull("task", "worker")
        self.assertIsNone(msg2)
        
        dlq = q.get_dlq("task", "worker")
        self.assertEqual(len(dlq), 1)
        self.assertEqual(dlq[0].payload, "fail_job")


class TestDurableQueue(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_produce_and_consume(self):
        q = DurableQueue(self.temp_dir, num_partitions=2)
        
        pid, offset = q.produce("user_123", "signup")
        
        msg = q.consume("group1", pid)
        self.assertIsNotNone(msg)
        self.assertEqual(msg.key, "user_123")
        self.assertEqual(msg.payload, "signup")
        self.assertEqual(msg.offset, offset)
        
        # Without commit, consuming again from same offset won't change
        msg_again = q.consume("group1", pid)
        self.assertEqual(msg_again.offset, offset)
        
        q.commit_offset("group1", pid, offset + 1)
        
        # After commit, consume should get nothing since no new messages
        self.assertIsNone(q.consume("group1", pid))

    def test_per_key_ordering(self):
        q = DurableQueue(self.temp_dir, num_partitions=4)
        
        p1, o1 = q.produce("keyA", "msg1")
        p2, o2 = q.produce("keyA", "msg2")
        
        # Same key must go to same partition
        self.assertEqual(p1, p2)
        # Offsets must be sequential
        self.assertTrue(o2 > o1)

    def test_durability(self):
        q1 = DurableQueue(self.temp_dir, num_partitions=1)
        p, o = q1.produce("k1", "data1")
        q1.commit_offset("g1", p, o + 1)
        
        # Simulate restart
        q2 = DurableQueue(self.temp_dir, num_partitions=1)
        
        # Group 'g1' should be at offset 1
        msg = q2.consume("g1", p)
        self.assertIsNone(msg)  # already committed
        
        # A new group should see the message from offset 0
        msg_new = q2.consume("g2", p)
        self.assertIsNotNone(msg_new)
        self.assertEqual(msg_new.payload, "data1")

    def test_idempotent_consumer(self):
        q = DurableQueue(self.temp_dir, num_partitions=1)
        pid, offset = q.produce("k1", "process_me")
        
        wrapper = IdempotentConsumerWrapper(q, "group_idem", max_retries=1)
        
        processed_count = 0
        def processor(payload):
            nonlocal processed_count
            processed_count += 1
            if processed_count == 1:
                raise Exception("Transient failure")
                
        # First attempt: processor fails
        success1 = wrapper.consume_and_process(pid, processor)
        self.assertFalse(success1)
        self.assertEqual(processed_count, 1)
        
        # Since it failed and exhausted max_retries (1), it should go to DLQ
        # Wait, wrapper max_retries=1 means it fails immediately and goes to DLQ?
        # Let's check wrapper logic.
        self.assertEqual(len(wrapper.dlq), 1)
        self.assertEqual(wrapper.dlq[0].payload, "process_me")
        
        # And it should commit the offset to move past the poison pill
        self.assertIsNone(q.consume("group_idem", pid))

if __name__ == '__main__':
    unittest.main()