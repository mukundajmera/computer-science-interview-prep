import os
import sys
import unittest
import time

BASE_DIR = os.path.dirname(__file__)
V1_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v1-basic"))
if V1_DIR not in sys.path:
    sys.path.insert(0, V1_DIR)

from view_event_ingestor import ViewEventIngestor, CountMinSketch


class ViewEventIngestorTest(unittest.TestCase):
    def setUp(self):
        self.service = ViewEventIngestor(k=3, window_sec=2.0)

    def test_cms_estimation(self):
        cms = CountMinSketch(width=100, depth=3)
        cms.add("vid1", 5)
        cms.add("vid2", 3)
        
        self.assertEqual(cms.estimate("vid1"), 5)
        self.assertEqual(cms.estimate("vid2"), 3)
        self.assertEqual(cms.estimate("vid3"), 0)

    def test_top_k_tracking(self):
        curr_time = 100.0
        # Ingest views
        for _ in range(5):
            self.service.ingest_view("v1", curr_time)
        for _ in range(3):
            self.service.ingest_view("v2", curr_time)
        for _ in range(4):
            self.service.ingest_view("v3", curr_time)
        for _ in range(2):
            self.service.ingest_view("v4", curr_time)
            
        top_k = self.service.get_top_k()
        self.assertEqual(len(top_k), 3)
        
        # Expected order: v1 (5), v3 (4), v2 (3)
        self.assertEqual(top_k[0][0], "v1")
        self.assertEqual(top_k[1][0], "v3")
        self.assertEqual(top_k[2][0], "v2")

    def test_decaying_sliding_window(self):
        # Window is 2.0 seconds
        curr = 100.0
        self.service.ingest_view("v1", curr)
        self.service.ingest_view("v1", curr)
        self.service.ingest_view("v2", curr)
        
        # Advance time by 1 sec
        curr = 101.0
        self.service.ingest_view("v2", curr)
        self.service.ingest_view("v2", curr)
        
        # Advance time past window for v1 (curr > 102.0)
        curr = 102.5
        # Trigger cleanup
        self.service.ingest_view("v3", curr)
        
        top_k = self.service.get_top_k()
        # v1 views (at 100.0) should be discarded.
        # Remaining: v2 (at 101.0) -> 2 views, v3 (at 102.5) -> 1 view
        
        counts = {vid: count for vid, count in top_k}
        self.assertEqual(counts.get("v2"), 2)
        self.assertEqual(counts.get("v3"), 1)
        self.assertTrue("v1" not in counts or counts["v1"] == 0)

    def test_heap_updates_correctly(self):
        curr = 10.0
        self.service.ingest_view("v1", curr)
        self.service.ingest_view("v2", curr)
        self.service.ingest_view("v3", curr)
        
        top = self.service.get_top_k()
        vids = set(v[0] for v in top)
        self.assertEqual(vids, {"v1", "v2", "v3"})
        
        # v4 comes in strong
        self.service.ingest_view("v4", curr)
        self.service.ingest_view("v4", curr)
        
        top = self.service.get_top_k()
        vids = set(v[0] for v in top)
        self.assertTrue("v4" in vids)
        self.assertEqual(len(top), 3)


if __name__ == "__main__":
    unittest.main()
