import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from kafka_broker_v2.partition_log import PartitionLogV2
from kafka_broker_v2.broker_cluster import BrokerClusterV2
from kafka_broker_v2.consumer_group_coordinator import ConsumerGroupCoordinatorV2


class TestKafkaBrokerV2Parity(unittest.TestCase):
    """The v1 test scenarios re-run against v2 to lock in v1 behavior."""

    def test_partition_log(self):
        log = PartitionLogV2(max_segment_bytes=50)
        msg1, msg2, msg3, msg4 = b"Hello Kafka 1", b"Hello Kafka 2", b"Hello Kafka 3", b"Hello Kafka 4"

        self.assertEqual(log.append(msg1), 0)
        self.assertEqual(log.append(msg2), 1)
        self.assertEqual(log.append(msg3), 2)
        self.assertEqual(log.append(msg4), 3)
        self.assertTrue(len(log.segments) > 1)

        msgs = log.read(start_offset=1, max_messages=2)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0][1], msg2)
        self.assertEqual(msgs[1][1], msg3)
        self.assertEqual(log.get_log_end_offset(), 4)

        log.truncate_to(3)
        self.assertEqual(log.get_log_end_offset(), 3)

        log.segments.pop(0)
        with self.assertRaises(ValueError):
            log.read(0, 10)
        with self.assertRaises(ValueError):
            log.read(5, 10)

    def test_broker_cluster_produce_fetch(self):
        cluster = BrokerClusterV2(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")

        cluster.produce("p1", b"msg1", acks=1)
        cluster.produce("p1", b"msg2", acks=-1)

        msgs = cluster.fetch("p1", 0, 10)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0], b"msg1")
        self.assertEqual(msgs[1], b"msg2")

    def test_insufficient_isr(self):
        cluster = BrokerClusterV2(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")

        cluster.fail_broker("broker2")
        cluster.fail_broker("broker3")

        with self.assertRaisesRegex(RuntimeError, "Insufficient ISR"):
            cluster.produce("p1", b"msg1", acks=-1)

    def test_broker_cluster_failover(self):
        cluster = BrokerClusterV2(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")

        cluster.produce("p1", b"msg1", acks=-1)
        cluster.fail_broker("broker1")

        self.assertTrue(cluster.partitions["p1"].leader_id in ["broker2", "broker3"])

        cluster.produce("p1", b"msg2", acks=-1)
        msgs = cluster.fetch("p1", 0, 10)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0], b"msg1")
        self.assertEqual(msgs[1], b"msg2")

    def test_deterministic_recovery(self):
        cluster = BrokerClusterV2(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")

        cluster.produce("p1", b"msg1", acks=1)
        cluster.fail_broker("broker1")
        cluster.produce("p1", b"msg2", acks=-1)
        cluster.recover_broker("broker1")

        msgs = cluster.fetch("p1", 0, 10)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0], b"msg2")

    def test_consumer_group_coordinator(self):
        coordinator = ConsumerGroupCoordinatorV2(heartbeat_timeout=0.1)
        coordinator.register_group("g1", ["p1", "p2", "p3"])
        coordinator.join_group("g1", "c1")
        coordinator.join_group("g1", "c2")

        total = len(coordinator.get_assignment("g1", "c1")) + len(coordinator.get_assignment("g1", "c2"))
        self.assertEqual(total, 3)

    def test_consumer_replay_and_bounded_retry(self):
        cluster = BrokerClusterV2(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")
        cluster.produce("p1", b"msg1", acks=-1)
        cluster.produce("p1", b"msg2", acks=-1)

        coordinator = ConsumerGroupCoordinatorV2(heartbeat_timeout=0.1)
        coordinator.register_group("g1", ["p1"])
        coordinator.join_group("g1", "c1")

        offset = coordinator.fetch_offset("g1", "p1")
        msgs = cluster.fetch("p1", offset, 1)
        self.assertEqual(msgs[0], b"msg1")
        coordinator.commit_offset("g1", "p1", offset + len(msgs))

        # Crash before commit: the offset still points at msg2.
        self.assertEqual(coordinator.fetch_offset("g1", "p1"), 1)


class TestKafkaBrokerV2(unittest.TestCase):
    """Tests for the three named v2 improvements."""

    # --- Improvement #1: retention policies + disk monitoring ---

    def test_size_based_retention_deletes_old_segments(self):
        log = PartitionLogV2(max_segment_bytes=50)
        for i in range(6):
            log.append(b"Hello Kafka %d" % i)  # 13 bytes each, rolls segments

        usage_before = log.disk_usage_bytes()
        self.assertGreater(usage_before, 50)
        deleted = log.enforce_retention(max_total_bytes=50)
        self.assertGreater(deleted, 0)
        self.assertLess(log.disk_usage_bytes(), usage_before)
        # Deleted offsets now hit the retention gap error.
        with self.assertRaisesRegex(ValueError, "OffsetOutOfRange"):
            log.read(0, 10)

    def test_retention_never_deletes_active_segment(self):
        log = PartitionLogV2(max_segment_bytes=50)
        log.append(b"only message")
        deleted = log.enforce_retention(max_total_bytes=0)
        self.assertEqual(deleted, 0)
        self.assertEqual(log.read(0, 1)[0][1], b"only message")

    def test_time_based_retention_uses_segment_age(self):
        now = [1000.0]
        log = PartitionLogV2(max_segment_bytes=50, clock=lambda: now[0])
        log.append(b"Hello Kafka 1")
        log.append(b"Hello Kafka 2")
        log.append(b"Hello Kafka 3")  # forces at least one rollover
        log.append(b"Hello Kafka 4")

        segment_count = len(log.segments)
        self.assertGreater(segment_count, 1)

        now[0] += 10_000.0  # every segment is now older than 5s
        deleted = log.enforce_retention(max_age_ms=5000.0)
        # All but the active segment are older than the retention window.
        self.assertEqual(deleted, segment_count - 1)
        self.assertEqual(len(log.segments), 1)

    # --- Improvement #2: idempotent producers ---

    def test_idempotent_produce_dedupes_retries(self):
        cluster = BrokerClusterV2(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")

        first = cluster.produce_idempotent("p1", b"msg1", acks=-1, producer_id="prod1", sequence=0)
        retry = cluster.produce_idempotent("p1", b"msg1", acks=-1, producer_id="prod1", sequence=0)

        self.assertEqual(first, retry)
        self.assertEqual(len(cluster.fetch("p1", 0, 10)), 1)  # appended once

    def test_idempotent_produce_rejects_sequence_gap(self):
        cluster = BrokerClusterV2(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")

        cluster.produce_idempotent("p1", b"msg1", acks=-1, producer_id="prod1", sequence=0)
        with self.assertRaisesRegex(ValueError, "OutOfOrderSequence"):
            cluster.produce_idempotent("p1", b"msg2", acks=-1, producer_id="prod1", sequence=2)

    def test_idempotent_sequences_are_per_producer(self):
        cluster = BrokerClusterV2(["broker1", "broker2", "broker3"])
        cluster.create_partition("p1", ["broker1", "broker2", "broker3"], "broker1")

        o1 = cluster.produce_idempotent("p1", b"a", acks=-1, producer_id="prod1", sequence=0)
        o2 = cluster.produce_idempotent("p1", b"b", acks=-1, producer_id="prod2", sequence=0)
        self.assertEqual((o1, o2), (0, 1))
        self.assertEqual(len(cluster.fetch("p1", 0, 10)), 2)

    # --- Improvement #3: injectable clock + lag metric ---

    def test_health_check_uses_injectable_clock(self):
        now = [1000.0]
        coordinator = ConsumerGroupCoordinatorV2(heartbeat_timeout=5.0, clock=lambda: now[0])
        coordinator.register_group("g1", ["p1", "p2", "p3"])
        coordinator.join_group("g1", "c1")
        coordinator.join_group("g1", "c2")

        now[0] += 6.0  # both members go quiet past the timeout
        coordinator.heartbeat("g1", "c1")  # only c1 is alive
        coordinator.check_health()

        self.assertEqual(len(coordinator.get_assignment("g1", "c1")), 3)
        self.assertEqual(coordinator.get_assignment("g1", "c2"), [])

    def test_consumer_lag_metric(self):
        coordinator = ConsumerGroupCoordinatorV2()
        coordinator.register_group("g1", ["p1"])
        coordinator.commit_offset("g1", "p1", 1)

        self.assertEqual(coordinator.consumer_lag("g1", "p1", log_end_offset=5), 4)
        coordinator.commit_offset("g1", "p1", 5)
        self.assertEqual(coordinator.consumer_lag("g1", "p1", log_end_offset=5), 0)


if __name__ == '__main__':
    unittest.main()
