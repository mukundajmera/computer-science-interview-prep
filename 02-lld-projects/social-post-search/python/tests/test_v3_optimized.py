import unittest
import sys
import os
import time

BASE_DIR = os.path.dirname(__file__)
V3_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v3-optimized"))
if V3_DIR not in sys.path:
    sys.path.insert(0, V3_DIR)

# Workaround for pytest cross-contamination
if 'post_ingestion_service_v3' in sys.modules:
    del sys.modules['post_ingestion_service_v3']
import importlib.util
spec = importlib.util.spec_from_file_location("post_ingestion_service_v3", os.path.join(V3_DIR, "post_ingestion_service_v3.py"))
post_ingestion_service_v3 = importlib.util.module_from_spec(spec)
sys.modules["post_ingestion_service_v3"] = post_ingestion_service_v3
spec.loader.exec_module(post_ingestion_service_v3)

from post_ingestion_service_v3 import PostIngestionServiceV3

class PostIngestionServiceV3Test(unittest.TestCase):
    def setUp(self):
        self.service = PostIngestionServiceV3()
        self.service.upsert("p1", "The quick brown fox jumps over the lazy dog.", "idemp1", "us-east")
        self.service.upsert("p2", "A fast brown fox leaps across a sleeping dog.", "idemp2", "us-east")
        self.service.upsert("p3", "Dogs are great companions for a walk in the park.", "idemp3", "us-east")
        self.service.upsert("p4", "Fox fox fox! Look at that fast brown fox!", "idemp4", "us-east")

    def test_idempotency(self):
        # Should return False because key was already used
        res = self.service.upsert("p1", "The quick brown fox jumps over the lazy dog.", "idemp1", "us-east")
        self.assertFalse(res)
        
        # New key should work
        res2 = self.service.upsert("p5", "Another test.", "idemp5", "us-east")
        self.assertTrue(res2)

    def test_boolean_and_search(self):
        results = self.service.search("brown AND fox", "us-east")
        self.assertEqual(results, ["p4", "p1", "p2"])
        
    def test_relevance_ranking(self):
        results = self.service.search("brown OR fox", "us-east")
        # p4 has highest score
        self.assertEqual(results, ["p4", "p1", "p2"])
        
    def test_empty_and_missing_terms(self):
        self.service.upsert("p5", "Just some random text without those keywords.", "idemp5", "us-east")
        # Empty tokens behavior
        self.assertEqual(self.service.search("", "us-east"), [])
        self.assertEqual(self.service.search("   ", "us-east"), [])
        
        # Missing term
        self.assertEqual(self.service.search("zebra", "us-east"), [])
        self.assertEqual(self.service.search("zebra AND fox", "us-east"), [])

    def test_deterministic_tie_order(self):
        # p1 and p2 have the exact same length and same number of matches for "brown OR fox"
        # Since Python sort uses (-score, post_id), tie should be resolved by ascending post_id.
        results = self.service.search("brown OR fox", "us-east")
        self.assertEqual(results, ["p4", "p1", "p2"])

    def test_deletes_and_updates(self):
        self.service.upsert("up1", "apple banana cherry", "idemp_up1", "us-east")
        self.assertEqual(["up1"], self.service.search("banana", "us-east"))
        
        # Update: change text to remove banana
        self.service.upsert("up1", "apple dog cherry", "idemp_up1_2", "us-east")
        self.assertEqual([], self.service.search("banana", "us-east"))
        self.assertEqual(["up1", "p1", "p2"], self.service.search("dog", "us-east"))
        
        # Delete
        self.service.delete("up1", "us-east")
        self.assertEqual(["p1", "p2"], self.service.search("dog", "us-east"))

if __name__ == "__main__":
    unittest.main()
