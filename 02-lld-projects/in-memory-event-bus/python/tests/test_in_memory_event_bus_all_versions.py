import unittest
import threading
import time
import sys
import os
import importlib.util

def get_in_memory_event_bus(version):
    spec = importlib.util.spec_from_file_location("in_memory_event_bus", os.path.join(os.path.dirname(__file__), "..", version, "in_memory_event_bus.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules["in_memory_event_bus_" + version] = module
    spec.loader.exec_module(module)
    if hasattr(module, "InMemoryEventBus"):
        return module.InMemoryEventBus
    return getattr(module, "EventBus", None)

class TestInMemoryEventBusAllVersionsBase(unittest.TestCase):
    def setUp(self):
        self.bus_class = getattr(self, "bus_class", None)
        if self.bus_class is None:
            self.skipTest("Base class")

    def test_deterministic_sequence_and_replay(self):
        bus = self.bus_class()
        bus.create_topic("topic1", 2)
        bus.subscribe("group1", "topic1")
        
        bus.publish("topic1", "msg1", 0)
        bus.publish("topic1", "msg2", 0)
        bus.publish("topic1", "msg3", 1)
        
        self.assertEqual(bus.poll("group1", "topic1", 0), "msg1")
        self.assertEqual(bus.poll("group1", "topic1", 1), "msg3")
        
        bus.commit_offset("group1", "topic1", 0, 1)
        self.assertEqual(bus.poll("group1", "topic1", 0), "msg2")
        self.assertEqual(bus.poll("group1", "topic1", 1), "msg3")

    def test_bounded_queue_block(self):
        bus = self.bus_class()
        bus.create_topic("topic1", 1)
        
        received = []
        latch = threading.Event()
        
        def handler(msg):
            received.append(msg)
            if len(received) == 3:
                latch.set()
            time.sleep(0.05)
            
        if hasattr(bus, "subscribe_push"):
            bus.subscribe_push("topic1", handler, 1, "BLOCK")
        else:
            bus.subscribe("topic1", handler, 1, "BLOCK")
        
        bus.publish("topic1", "msg1", 0)
        bus.publish("topic1", "msg2", 0)
        bus.publish("topic1", "msg3", 0)
        
        latch.wait(timeout=2.0)
        self.assertEqual(len(received), 3)
        bus.unsubscribe_all()

    def test_bounded_queue_drop(self):
        bus = self.bus_class()
        bus.create_topic("topic1", 1)
        
        count = [0]
        
        def handler(msg):
            count[0] += 1
            time.sleep(0.1)
            
        if hasattr(bus, "subscribe_push"):
            bus.subscribe_push("topic1", handler, 1, "DROP")
        else:
            bus.subscribe("topic1", handler, 1, "DROP")
        
        bus.publish("topic1", "msg1", 0)
        bus.publish("topic1", "msg2", 0)
        bus.publish("topic1", "msg3", 0)
        
        time.sleep(0.5)
        self.assertTrue(count[0] < 3)
        bus.unsubscribe_all()

    def test_bounded_queue_reject(self):
        bus = self.bus_class()
        bus.create_topic("topic1", 1)
        
        def handler(msg):
            time.sleep(0.5)
            
        if hasattr(bus, "subscribe_push"):
            bus.subscribe_push("topic1", handler, 1, "REJECT")
        else:
            bus.subscribe("topic1", handler, 1, "REJECT")
        
        bus.publish("topic1", "msg1", 0)
        with self.assertRaises(RuntimeError):
            bus.publish("topic1", "msg2", 0)
            bus.publish("topic1", "msg3", 0)
            
        bus.unsubscribe_all()

class TestInMemoryEventBusV1(TestInMemoryEventBusAllVersionsBase):
    bus_class = get_in_memory_event_bus("v1-basic")

class TestInMemoryEventBusV2(TestInMemoryEventBusAllVersionsBase):
    bus_class = get_in_memory_event_bus("v2-extended")

class TestInMemoryEventBusV3(TestInMemoryEventBusAllVersionsBase):
    bus_class = get_in_memory_event_bus("v3-optimized")

if __name__ == '__main__':
    unittest.main()
