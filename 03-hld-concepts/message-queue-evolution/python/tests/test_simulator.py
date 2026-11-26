import unittest
import sys
import os

# Add the module path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from simulator import MessageQueueEvolutionSimulator

class TestMessageQueueEvolutionSimulator(unittest.TestCase):
    def setUp(self):
        self.sim = MessageQueueEvolutionSimulator()

    def test_amqp_topic_routing_and_ack(self):
        self.sim.create_exchange("events_tx", "topic")
        self.sim.create_queue("orders_q")
        self.sim.create_queue("all_events_q")
        
        self.sim.bind_queue("events_tx", "orders_q", "order.*")
        self.sim.bind_queue("events_tx", "all_events_q", "#")
        
        self.sim.publish_amqp("events_tx", "order.created", "Order 123")
        self.sim.publish_amqp("events_tx", "user.signup", "User Bob")
        
        # orders_q should only have order.created
        self.assertEqual(len(self.sim.queues["orders_q"]), 1)
        # all_events_q should have both
        self.assertEqual(len(self.sim.queues["all_events_q"]), 2)
        
        # Test consumption and ACK (removes from queue)
        msg = self.sim.consume_amqp("orders_q")
        self.assertEqual(msg["msg"], "Order 123")
        
        self.sim.ack_amqp("orders_q")
        self.assertEqual(len(self.sim.queues["orders_q"]), 0) # Removed after ACK

    def test_kafka_partition_append_and_offset(self):
        self.sim.create_topic_partitions("clicks", 2)
        
        o1 = self.sim.publish_kafka("clicks", 0, "Click A")
        o2 = self.sim.publish_kafka("clicks", 0, "Click B")
        
        self.assertEqual(o1, 0)
        self.assertEqual(o2, 1)
        
        # Consumer gets first message
        msg1 = self.sim.consume_kafka("clicks", 0, "cg1")
        self.assertEqual(msg1["msg"], "Click A")
        
        # If not committed, consumes same message again
        msg1_again = self.sim.consume_kafka("clicks", 0, "cg1")
        self.assertEqual(msg1_again["msg"], "Click A")
        
        # Commit and consume next
        self.sim.commit_offset_kafka("clicks", 0, "cg1", msg1["offset"])
        msg2 = self.sim.consume_kafka("clicks", 0, "cg1")
        self.assertEqual(msg2["msg"], "Click B")

    def test_kafka_offset_replay(self):
        self.sim.create_topic_partitions("metrics", 1)
        for i in range(5):
            self.sim.publish_kafka("metrics", 0, f"Metric {i}")
            
        for i in range(5):
            msg = self.sim.consume_kafka("metrics", 0, "analytics_group")
            self.sim.commit_offset_kafka("metrics", 0, "analytics_group", msg["offset"])
            
        # Verify no more messages
        self.assertIsNone(self.sim.consume_kafka("metrics", 0, "analytics_group"))
        
        # Time travel back to offset 2
        self.sim.replay_kafka("metrics", 0, "analytics_group", 2)
        msg_replay = self.sim.consume_kafka("metrics", 0, "analytics_group")
        self.assertEqual(msg_replay["msg"], "Metric 2")

    def test_pulsar_segment_roll_and_cold_tier(self):
        topic_partition = "logs-partition-0"
        
        # Publish 8 messages. Segment size is 3.
        # This will create 2 full segments (6 msgs) in tiered storage, and 2 in active ledger.
        for i in range(8):
            self.sim.publish_pulsar(topic_partition, f"Log {i}")
            
        self.assertEqual(len(self.sim.tiered_storage[topic_partition]), 2)
        self.assertEqual(len(self.sim.active_ledgers[topic_partition]), 2)
        
        # Consume index 1 (Cold storage, Segment 0)
        msg_cold1 = self.sim.consume_pulsar(topic_partition, 1)
        self.assertEqual(msg_cold1["source"], "S3_TIERED")
        self.assertEqual(msg_cold1["msg"], "Log 1")
        
        # Consume index 4 (Cold storage, Segment 1)
        msg_cold2 = self.sim.consume_pulsar(topic_partition, 4)
        self.assertEqual(msg_cold2["source"], "S3_TIERED")
        self.assertEqual(msg_cold2["msg"], "Log 4")
        
        # Consume index 7 (Active ledger)
        msg_active = self.sim.consume_pulsar(topic_partition, 7)
        self.assertEqual(msg_active["source"], "ACTIVE_BOOKIE")
        self.assertEqual(msg_active["msg"], "Log 7")

if __name__ == '__main__':
    unittest.main()
