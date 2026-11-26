import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-realistic')))
from partitioned_log import Topic, ConsumerGroup

class TestV2PartitionedLog(unittest.TestCase):
    def setUp(self):
        self.topic = Topic("test_topic", num_partitions=3)
        self.group = ConsumerGroup(self.topic, "test_group")
        
    def test_produce(self):
        offset = self.topic.produce(0, "msg1")
        self.assertEqual(offset, 0)
        
    def test_consume(self):
        self.topic.produce(0, "msg1")
        msg = self.group.poll(0)
        self.assertEqual(msg, "msg1")
        
    def test_consume_empty(self):
        msg = self.group.poll(0)
        self.assertIsNone(msg)
        
    def test_consume_multiple(self):
        self.topic.produce(0, "msg1")
        self.topic.produce(0, "msg2")
        self.assertEqual(self.group.poll(0), "msg1")
        self.assertEqual(self.group.poll(0), "msg2")
        
    def test_partition_isolation(self):
        self.topic.produce(0, "p0_msg")
        self.topic.produce(1, "p1_msg")
        self.assertEqual(self.group.poll(0), "p0_msg")
        self.assertEqual(self.group.poll(1), "p1_msg")
