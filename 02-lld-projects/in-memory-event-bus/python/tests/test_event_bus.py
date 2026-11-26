import unittest
import sys
import os
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def get_module(version, module_name):
    import importlib.util
    dir_path = os.path.join(os.path.dirname(__file__), '..', version)
    file_path = os.path.join(dir_path, f'{module_name}.py')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

class TestEventBus(unittest.TestCase):

    def test_v1_basic(self):
        event_bus_mod = get_module("v1-basic", "in_memory_event_bus")
        EventBus = getattr(event_bus_mod, "InMemoryEventBus", None)
        if EventBus is None:
             EventBus = getattr(event_bus_mod, "EventBus", None)
        if EventBus is None:
             self.skipTest("No eventbus found")
        bus = EventBus()
        bus.create_topic("test")
        events = []
        if hasattr(bus, "subscribe_push"):
             bus.subscribe_push("test", lambda e: events.append(e), 10, "BLOCK")
        else:
             bus.subscribe("test", lambda e: events.append(e), 10, "BLOCK")
        bus.publish("test", "hello")
        
        import time
        time.sleep(0.1)
        self.assertEqual(events, ["hello"])
        bus.unsubscribe_all()

    def test_v2_extended(self):
        event_bus_mod = get_module("v2-extended", "in_memory_event_bus")
        EventBus = event_bus_mod.InMemoryEventBus
        bus = EventBus()
        bus.create_topic("test", 2)
        bus.subscribe("g1", "test")
        
        bus.publish("test", "msg1", 0)
        bus.publish("test", "msg2", 1)
        
        self.assertEqual(bus.poll("g1", "test", 0), "msg1")
        self.assertEqual(bus.poll("g1", "test", 1), "msg2")
        
        bus.commit_offset("g1", "test", 0, 1)
        bus.commit_offset("g1", "test", 1, 1)

    def test_v3_optimized(self):
        event_bus_mod = get_module("v3-optimized", "in_memory_event_bus")
        EventBus = getattr(event_bus_mod, "InMemoryEventBus", None)
        bus = EventBus()
        bus.create_topic("test", 1)
        bus.subscribe("g1", "test")
        
        bus.publish("test", "msg1", 0)
        self.assertEqual(bus.poll("g1", "test", 0), "msg1")
        
        bus.fail_event("g1", "test", "msg1")
        self.assertEqual(bus.poll("g1", "test", 0), "msg1")

    def test_v3_dlq(self):
        event_bus_mod = get_module("v3-optimized", "in_memory_event_bus")
        EventBus = getattr(event_bus_mod, "InMemoryEventBus", None)
        bus = EventBus()
        bus.create_topic("test", 1)
        bus.subscribe("g1", "test")
        
        bus.publish("test", "msg1", 0)
        
        bus.fail_event("g1", "test", "msg1")
        bus.fail_event("g1", "test", "msg1")
        bus.fail_event("g1", "test", "msg1")
        bus.fail_event("g1", "test", "msg1")
        
        self.assertTrue("g1_test" in bus.dlq)
        self.assertTrue("msg1" in bus.dlq["g1_test"])

    def test_v2_multiple_groups(self):
        event_bus_mod = get_module("v2-extended", "in_memory_event_bus")
        EventBus = event_bus_mod.InMemoryEventBus
        bus = EventBus()
        bus.create_topic("test", 1)
        
        bus.subscribe("g1", "test")
        bus.subscribe("g2", "test")
        
        bus.publish("test", "msg1", 0)
        
        self.assertEqual(bus.poll("g1", "test", 0), "msg1")
        self.assertEqual(bus.poll("g2", "test", 0), "msg1")
        
        bus.commit_offset("g1", "test", 0, 1)
        
        self.assertIsNone(bus.poll("g1", "test", 0))
        self.assertEqual(bus.poll("g2", "test", 0), "msg1")

    def test_v2_concurrent_publish(self):
        event_bus_mod = get_module("v2-extended", "in_memory_event_bus")
        EventBus = event_bus_mod.InMemoryEventBus
        bus = EventBus()
        bus.create_topic("test", 4)
        
        def pub(idx):
            for i in range(100):
                bus.publish("test", f"msg_{idx}_{i}", idx)
                
        threads = []
        for i in range(4):
            t = threading.Thread(target=pub, args=(i,))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        for i in range(4):
            self.assertEqual(len(bus.topics["test"].partitions[i].events), 100)

if __name__ == '__main__':
    unittest.main()
