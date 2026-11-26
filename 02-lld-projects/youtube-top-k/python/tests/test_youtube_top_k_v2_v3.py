import os
import sys
import unittest
import time

BASE_DIR = os.path.dirname(__file__)
V2_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v2-extended"))
V3_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v3-optimized"))

if V2_DIR not in sys.path:
    sys.path.insert(0, V2_DIR)
if V3_DIR not in sys.path:
    sys.path.insert(0, V3_DIR)

# Clean sys.modules if they have conflicting names across directories
if 'view_event_ingestor_v2' in sys.modules:
    del sys.modules['view_event_ingestor_v2']
if 'view_event_ingestor_v3' in sys.modules:
    del sys.modules['view_event_ingestor_v3']
if 'window_state_store' in sys.modules:
    del sys.modules['window_state_store']

import importlib.util

spec2 = importlib.util.spec_from_file_location("view_event_ingestor_v2", os.path.join(V2_DIR, "view_event_ingestor_v2.py"))
v2 = importlib.util.module_from_spec(spec2)
sys.modules["view_event_ingestor_v2"] = v2
spec2.loader.exec_module(v2)

spec3 = importlib.util.spec_from_file_location("view_event_ingestor_v3", os.path.join(V3_DIR, "view_event_ingestor_v3.py"))
v3 = importlib.util.module_from_spec(spec3)
sys.modules["view_event_ingestor_v3"] = v3
spec3.loader.exec_module(v3)

class MockWindowStateStore:
    def __init__(self):
        self.store = {}
    def save(self, window_key: str, state_payload: str) -> None:
        self.store[window_key] = state_payload
    def load(self, window_key: str):
        return self.store.get(window_key)

class MockIdempotencyStore:
    def __init__(self):
        self.claims = set()
    def claim(self, key: str, ttl_ms: int) -> bool:
        if key in self.claims:
            return False
        self.claims.add(key)
        return True

class MockDistributedRepository:
    def __init__(self):
        self.store = {}
    def save(self, key: str, value: str, region: str) -> None:
        self.store[(key, region)] = value
    def find(self, key: str, region: str):
        return self.store.get((key, region))

class V2Test(unittest.TestCase):
    def setUp(self):
        self.store = MockWindowStateStore()
        self.service = v2.ViewEventIngestorV2(self.store, k=3)

    def test_v2_ingest_and_top_k(self):
        curr_time = 1000
        for _ in range(5):
            self.service.ingest("v1", curr_time)
        for _ in range(3):
            self.service.ingest("v2", curr_time)
        for _ in range(4):
            self.service.ingest("v3", curr_time)
        for _ in range(2):
            self.service.ingest("v4", curr_time)
            
        window_key = self.service._get_window_key(curr_time)
        top_k = self.service.top_k(window_key, 3)
        self.assertEqual(len(top_k), 3)
        
        # Expected order: v1, v3, v2
        self.assertEqual(top_k[0], "v1")
        self.assertEqual(top_k[1], "v3")
        self.assertEqual(top_k[2], "v2")


    def test_v2_tie_breaking(self):
        curr_time = 2000
        self.service.ingest("vA", curr_time)
        self.service.ingest("vB", curr_time)
        self.service.ingest("vC", curr_time)
        
        window_key = self.service._get_window_key(curr_time)
        top_k = self.service.top_k(window_key, 2)
        
        # Tie broken by video_id ascending
        self.assertEqual(len(top_k), 2)
        self.assertEqual(top_k[0], "vA")
        self.assertEqual(top_k[1], "vB")

    def test_v2_empty_stream(self):
        top_k = self.service.top_k("non_existent_window", 3)
        self.assertEqual(len(top_k), 0)

    def test_v2_exact_stream_comparison(self):
        curr_time = 3000
        # Reference counts: v1: 50, v2: 20, v3: 10, v4: 5
        for _ in range(50): self.service.ingest("v1", curr_time)
        for _ in range(20): self.service.ingest("v2", curr_time)
        for _ in range(10): self.service.ingest("v3", curr_time)
        for _ in range(5):  self.service.ingest("v4", curr_time)
        
        window_key = self.service._get_window_key(curr_time)
        top_k = self.service.top_k(window_key, 3)
        
        self.assertEqual(len(top_k), 3)
        self.assertEqual(top_k[0], "v1")
        self.assertEqual(top_k[1], "v2")
        self.assertEqual(top_k[2], "v3")

    def test_v2_window_rotation_and_bounds(self):
        base_time = 4000 * 3600 * 1000 # 4000 hours in ms
        # Ingest into 6 distinct windows
        for i in range(6):
            time_ms = base_time + (i * 3600 * 1000)
            self.service.ingest(f"v{i}", time_ms)
        
        # Max windows is 5, so the first window (i=0) should be evicted from memory
        window_key_0 = self.service._get_window_key(base_time)
        self.assertTrue(window_key_0 not in self.service.windows)
        
        # We can still load it from the store because we serialized it
        top_k_0 = self.service.top_k(window_key_0, 1)
        self.assertEqual(len(top_k_0), 1)
        self.assertEqual(top_k_0[0], "v0")

    def test_v2_rollback_ignored(self):
        ws = v2.WindowState(1000, 5)
        ws.cms.add("v1", -1)
        self.assertEqual(ws.cms.estimate("v1"), 0)

class V3Test(unittest.TestCase):
    def setUp(self):
        self.repo = MockDistributedRepository()
        self.idemp = MockIdempotencyStore()
        self.service = v3.ViewEventIngestorV3(self.repo, self.idemp, k=3)

    def test_v3_idempotency(self):
        curr_time = 1000
        
        # First ingest succeeds
        self.assertTrue(self.service.ingest("v1", curr_time, "event1", "us-east"))
        
        # Duplicate fails
        self.assertFalse(self.service.ingest("v1", curr_time, "event1", "us-east"))
        
        # Different event succeeds
        self.assertTrue(self.service.ingest("v1", curr_time, "event2", "us-east"))
        
        # Another video
        self.assertTrue(self.service.ingest("v2", curr_time, "event3", "us-east"))
        
        window_key = self.service._get_window_key(curr_time)
        top_k = self.service.top_k(window_key, 2, "us-east")
        self.assertEqual(len(top_k), 2)
        self.assertEqual(top_k[0], "v1")
        self.assertEqual(top_k[1], "v2")

    def test_v3_tie_breaking(self):
        curr_time = 2000
        self.service.ingest("vA", curr_time, "ev1", "us-east")
        self.service.ingest("vB", curr_time, "ev2", "us-east")
        self.service.ingest("vC", curr_time, "ev3", "us-east")
        
        window_key = self.service._get_window_key(curr_time)
        top_k = self.service.top_k(window_key, 2, "us-east")
        
        self.assertEqual(len(top_k), 2)
        self.assertEqual(top_k[0], "vA")
        self.assertEqual(top_k[1], "vB")

    def test_v3_empty_stream(self):
        top_k = self.service.top_k("non_existent_window", 3, "us-east")
        self.assertEqual(len(top_k), 0)

    def test_v3_exact_stream_comparison(self):
        curr_time = 3000
        region_str = "us-east"
        for i in range(50): self.service.ingest("v1", curr_time, f"e1_{i}", region_str)
        for i in range(20): self.service.ingest("v2", curr_time, f"e2_{i}", region_str)
        for i in range(10): self.service.ingest("v3", curr_time, f"e3_{i}", region_str)
        for i in range(5):  self.service.ingest("v4", curr_time, f"e4_{i}", region_str)
        
        window_key = self.service._get_window_key(curr_time)
        top_k = self.service.top_k(window_key, 3, region_str)
        
        self.assertEqual(len(top_k), 3)
        self.assertEqual(top_k[0], "v1")
        self.assertEqual(top_k[1], "v2")
        self.assertEqual(top_k[2], "v3")

    def test_v3_window_rotation_and_bounds(self):
        base_time = 4000 * 3600 * 1000
        for i in range(6):
            time_ms = base_time + (i * 3600 * 1000)
            self.service.ingest(f"v{i}", time_ms, f"ev_{i}", "us-east")
        
        window_key_0 = self.service._get_window_key(base_time)
        self.assertTrue(window_key_0 not in self.service.windows)
        
        top_k_0 = self.service.top_k(window_key_0, 1, "us-east")
        self.assertEqual(len(top_k_0), 1)
        self.assertEqual(top_k_0[0], "v0")

    def test_v3_rollback_ignored(self):
        ws = v3.WindowState(1000, 5)
        ws.cms.add("v1", -1)
        self.assertEqual(ws.cms.estimate("v1"), 0)


if __name__ == "__main__":
    unittest.main()
