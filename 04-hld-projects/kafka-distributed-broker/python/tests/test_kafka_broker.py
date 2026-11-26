import unittest
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from kafka_broker.partition_log import PartitionLog
from kafka_broker.broker_cluster import BrokerCluster
from kafka_broker.consumer_group_coordinator import ConsumerGroupCoordinator

class TestKafkaBroker(unittest.TestCase):
    def test_partition_log(self):
        log = PartitionLog(max_segment_bytes=50)
        msg1 = b"Hello Kafka 1"
        msg2 = b"Hello Kafka 2"
        msg3 = b"Hello Kafka 3"
        msg4 = b"Hello Kafka 4"
        
        offset1 = log.append(msg1)
        offset2 = log.append(msg2)
        offset3 = log.append(msg3)
        offset4 = log.append(msg4)
        
        self.assertEqual(offset1, 0)
        self.assertEqual(offset2, 1)
        self.assertEqual(offset3, 2)
        self.assertEqual(offset4, 3)
        self.assertTrue(len(log.segments) > 1)
        
        msgs = log.read(start_offset=1, max_messages=2)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0][1], msg2)
        self.assertEqual(msgs[1][1], msg3)
        
        self.assertEqual(log.get_log_end_offset(), 4)

        # Truncate tail simulation
        log.truncate_to(3)
        self.assertEqual(log.get_log_end_offset(), 3)
        
        # Retention gap simulation
        log.segments.pop(0) # Drops offset 0, 1 (depending on segment max bytes)
        with self.assertRaises(ValueError):
            log.read(0, 10)
            
        with self.assertRaises(ValueError):
            log.read(5, 10)

    def test_broker_cluster_produce_fetch(self):
        cluster = BrokerCluster(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")
        
        cluster.produce("p1", b"msg1", acks=1)
        cluster.produce("p1", b"msg2", acks=-1)
        
        msgs = cluster.fetch("p1", 0, 10)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0], b"msg1")
        self.assertEqual(msgs[1], b"msg2")

    def test_insufficient_isr(self):
        cluster = BrokerCluster(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")
        
        cluster.fail_broker("broker2")
        cluster.fail_broker("broker3")
        
        with self.assertRaisesRegex(RuntimeError, "Insufficient ISR"):
            cluster.produce("p1", b"msg1", acks=-1)

    def test_broker_cluster_failover(self):
        cluster = BrokerCluster(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")
        
        cluster.produce("p1", b"msg1", acks=-1)
        cluster.fail_broker("broker1")
        
        p_info = cluster.partitions["p1"]
        self.assertTrue(p_info.leader_id in ["broker2", "broker3"])
        
        cluster.produce("p1", b"msg2", acks=-1)
        
        msgs = cluster.fetch("p1", 0, 10)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0], b"msg1")
        self.assertEqual(msgs[1], b"msg2")

    def test_deterministic_recovery(self):
        cluster = BrokerCluster(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")
        
        cluster.produce("p1", b"msg1", acks=1)
        cluster.fail_broker("broker1")
        
        cluster.produce("p1", b"msg2", acks=-1)
        
        cluster.recover_broker("broker1")
        
        msgs = cluster.fetch("p1", 0, 10)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0], b"msg2")

    def test_consumer_group_coordinator(self):
        coordinator = ConsumerGroupCoordinator(heartbeat_timeout=0.1)
        coordinator.register_group("g1", ["p1", "p2", "p3"])
        
        coordinator.join_group("g1", "c1")
        coordinator.join_group("g1", "c2")
        
        c1_assignment = coordinator.get_assignment("g1", "c1")
        c2_assignment = coordinator.get_assignment("g1", "c2")
        self.assertEqual(len(c1_assignment) + len(c2_assignment), 3)
        
        time.sleep(0.2)
        coordinator.heartbeat("g1", "c1")
        coordinator.check_health()
        
        c1_assignment_new = coordinator.get_assignment("g1", "c1")
        self.assertEqual(len(c1_assignment_new), 3)

    def test_consumer_replay_and_bounded_retry(self):
        cluster = BrokerCluster(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")

        cluster.produce("p1", b"msg1", acks=-1)
        cluster.produce("p1", b"msg2", acks=-1)
        cluster.produce("p1", b"msg3", acks=-1)

        coordinator = ConsumerGroupCoordinator(heartbeat_timeout=0.1)
        coordinator.register_group("g1", ["p1"])
        coordinator.join_group("g1", "c1")

        # 1. Group progression (successful fetch and commit)
        fetch_offset = coordinator.fetch_offset("g1", "p1")
        self.assertEqual(fetch_offset, 0)

        msgs = cluster.fetch("p1", fetch_offset, 1)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0], b"msg1")

        coordinator.commit_offset("g1", "p1", fetch_offset + len(msgs))

        # 2. Duplicate replay (crashing before commit, refetching, and processing duplicates)
        # Fetch msg2 and msg3
        fetch_offset = coordinator.fetch_offset("g1", "p1")
        self.assertEqual(fetch_offset, 1)
        
        msgs = cluster.fetch("p1", fetch_offset, 2)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0], b"msg2")
        self.assertEqual(msgs[1], b"msg3")

        # Simulating crash before commit: we DO NOT call commit_offset.
        
        # Re-fetch due to crash (duplicate replay)
        refetch_offset = coordinator.fetch_offset("g1", "p1")
        self.assertEqual(refetch_offset, 1) # Still 1 since we didn't commit

        duplicate_msgs = cluster.fetch("p1", refetch_offset, 2)
        self.assertEqual(len(duplicate_msgs), 2)
        self.assertEqual(duplicate_msgs[0], b"msg2")
        self.assertEqual(duplicate_msgs[1], b"msg3")

        # Now commit successfully
        coordinator.commit_offset("g1", "p1", refetch_offset + len(duplicate_msgs))

        # 3. Bounded shutdown (finite retry loops to avoid hangs)
        # Simulate checking for new messages with bounded retries
        retry_count = 0
        max_retries = 3
        final_msgs = []
        
        while retry_count < max_retries:
            current_offset = coordinator.fetch_offset("g1", "p1")
            final_msgs = cluster.fetch("p1", current_offset, 10)
            if final_msgs:
                break
            retry_count += 1
            # Normally would sleep or backoff here
        
        self.assertEqual(retry_count, max_retries) # Should exhaust retries as no new messages are produced
        self.assertEqual(len(final_msgs), 0)

if __name__ == '__main__':
    unittest.main()
