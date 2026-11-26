import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-production')))
from replicated_log import ReplicatedPartition

class TestV3ReplicatedLog(unittest.TestCase):
    def setUp(self):
        self.partition = ReplicatedPartition(0, 1, [2, 3])
        
    def test_append_acks_all(self):
        offset = self.partition.append("msg", acks="all")
        self.assertEqual(offset, 0)
        self.assertEqual(self.partition.high_watermark, 1)
        
    def test_not_enough_replicas(self):
        self.partition.fail_node(2)
        self.partition.fail_node(3)
        with self.assertRaises(Exception):
            self.partition.append("msg", acks="all", min_insync_replicas=2)
            
    def test_leader_failover(self):
        self.partition.fail_node(1)
        self.assertIn(self.partition.leader_id, [2, 3])
        
    def test_leader_failover_empty_isr(self):
        self.partition.fail_node(1)
        self.partition.fail_node(2)
        self.partition.fail_node(3)
        self.assertIsNone(self.partition.leader_id)
        
    def test_append_acks_1(self):
        offset = self.partition.append("msg", acks="1")
        self.assertEqual(offset, 0)
        self.assertEqual(self.partition.high_watermark, 0)
