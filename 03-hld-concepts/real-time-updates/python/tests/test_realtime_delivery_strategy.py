"""Unit Tests for Realtime Delivery Implementations."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-realistic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-production'))

from realtime_channel_selector import RealtimeChannelSelector, DeliveryMode
from connection_registry import ConnectionRegistry
from distributed_realtime_router import RealtimeUpdateCoordinator

class TestRealtimeDelivery(unittest.TestCase):
    
    # v1-simple
    def test_channel_selector_websocket(self):
        selector = RealtimeChannelSelector()
        self.assertEqual(selector.choose(True, True, True), DeliveryMode.WEBSOCKET)
        
    def test_channel_selector_sse(self):
        selector = RealtimeChannelSelector()
        self.assertEqual(selector.choose(False, True, True), DeliveryMode.SSE)

    # v2-realistic
    def test_connection_registry_subscribe(self):
        registry = ConnectionRegistry()
        registry.subscribe("topic1", "conn1")
        registry.subscribe("topic1", "conn2")
        self.assertEqual(registry.connections_for_topic("topic1"), ["conn1", "conn2"])
        
    def test_connection_registry_unsubscribe(self):
        registry = ConnectionRegistry()
        registry.subscribe("topic1", "conn1")
        registry.unsubscribe("topic1", "conn1")
        self.assertEqual(registry.connections_for_topic("topic1"), [])

    # v3-production
    def test_update_coordinator_publish(self):
        registry = ConnectionRegistry()
        registry.subscribe("topic1", "conn1")
        
        pushed = []
        def push_adapter(conn, payload):
            pushed.append((conn, payload))
            
        coord = RealtimeUpdateCoordinator(registry, push_adapter)
        coord.publish("topic1", "msg1", 1)
        
        self.assertEqual(len(pushed), 1)
        self.assertEqual(pushed[0], ("conn1", "msg1"))
        
    def test_update_coordinator_ignore_old_offset(self):
        registry = ConnectionRegistry()
        registry.subscribe("topic1", "conn1")
        
        pushed = []
        def push_adapter(conn, payload):
            pushed.append((conn, payload))
            
        coord = RealtimeUpdateCoordinator(registry, push_adapter)
        coord.publish("topic1", "msg1", 2)
        coord.publish("topic1", "msg2", 1) # should be ignored
        
        self.assertEqual(len(pushed), 1)
        self.assertEqual(pushed[0], ("conn1", "msg1"))

    def test_resume_missed_messages(self):
        registry = ConnectionRegistry()
        
        pushed = []
        def push_adapter(conn, payload):
            pushed.append((conn, payload))
            
        coord = RealtimeUpdateCoordinator(registry, push_adapter)
        
        # Publish some messages while client is disconnected
        coord.publish("topic1", "msg1", 1)
        coord.publish("topic1", "msg2", 2)
        coord.publish("topic1", "msg3", 3)
        
        # Client reconnects and provides last known offset 1
        coord.resume_from("conn1", 1, "topic1")
        
        # Should receive exactly msg2 and msg3
        self.assertEqual(len(pushed), 2)
        self.assertEqual(pushed[0], ("conn1", "msg2"))
        self.assertEqual(pushed[1], ("conn1", "msg3"))
        
        # Further publications should work normally
        coord.publish("topic1", "msg4", 4)
        self.assertEqual(len(pushed), 3)
        self.assertEqual(pushed[2], ("conn1", "msg4"))

    def test_slow_consumer(self):
        registry = ConnectionRegistry()
        registry.subscribe("topic1", "conn1")
        
        pushed = []
        def push_adapter(conn, payload):
            if payload == "msg2":
                raise Exception("SlowConsumer")
            pushed.append((conn, payload))
            
        coord = RealtimeUpdateCoordinator(registry, push_adapter)
        
        coord.publish("topic1", "msg1", 1)
        self.assertEqual(len(pushed), 1)
        
        coord.publish("topic1", "msg2", 2) # Triggers SlowConsumer exception
        self.assertEqual(len(pushed), 1)
        
        coord.publish("topic1", "msg3", 3) # Should be skipped because disconnected
        self.assertEqual(len(pushed), 1)
        
        # Test resuming after being a slow consumer
        pushed.clear()
        
        # Update push_adapter so it doesn't fail anymore for the test
        def successful_push_adapter(conn, payload):
            pushed.append((conn, payload))
        coord._push_adapter = successful_push_adapter
        
        coord.resume_from("conn1", 1, "topic1")
        # Should push msg2 and msg3 on resume
        self.assertEqual(len(pushed), 2)
        self.assertEqual(pushed[0], ("conn1", "msg2"))
        self.assertEqual(pushed[1], ("conn1", "msg3"))

if __name__ == '__main__':
    unittest.main()
