import unittest
import sys
import os

BASE_DIR = os.path.dirname(__file__)
V2_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v2-extended"))
if V2_DIR not in sys.path:
    sys.path.insert(0, V2_DIR)

# Workaround for pytest cross-contamination
if 'post_ingestion_service_v2' in sys.modules:
    del sys.modules['post_ingestion_service_v2']
import importlib.util
spec = importlib.util.spec_from_file_location("post_ingestion_service_v2", os.path.join(V2_DIR, "post_ingestion_service_v2.py"))
post_ingestion_service_v2 = importlib.util.module_from_spec(spec)
sys.modules["post_ingestion_service_v2"] = post_ingestion_service_v2
spec.loader.exec_module(post_ingestion_service_v2)

from post_ingestion_service_v2 import PostIngestionServiceV2

class PostIngestionServiceV2Test(unittest.TestCase):
    def setUp(self):
        self.service = PostIngestionServiceV2()
        self.service.upsert("p1", "The quick brown fox jumps over the lazy dog.")
        self.service.upsert("p2", "A fast brown fox leaps across a sleeping dog.")
        self.service.upsert("p3", "Dogs are great companions for a walk in the park.")
        self.service.upsert("p4", "Fox fox fox! Look at that fast brown fox!")

    def test_boolean_and_search(self):
        results = self.service.search("brown AND fox")
        self.assertEqual(results, ["p4", "p1", "p2"])
        
        results_lazy = self.service.search("lazy AND dog")
        self.assertEqual(results_lazy, ["p1"])
        
        results_none = self.service.search("fox AND elephant")
        self.assertEqual(results_none, [])

    def test_boolean_or_search(self):
        results = self.service.search("lazy OR companions")
        self.assertEqual(results, ["p3", "p1"])
        
        results_fox = self.service.search("fox")
        self.assertEqual(results_fox, ["p4", "p1", "p2"])

    def test_relevance_ranking(self):
        results = self.service.search("brown OR fox")
        self.assertEqual(results, ["p4", "p1", "p2"])

    def test_empty_and_missing_terms(self):
        self.assertEqual(self.service.search(""), [])
        self.assertEqual(self.service.search("the and or"), [])
        self.assertEqual(self.service.search("missingterm"), [])

    def test_deterministic_tie_order(self):
        self.service.upsert("t1", "apple")
        self.service.upsert("t2", "apple")
        self.service.upsert("t3", "apple")
        # All three have exact same content and doc length, so score will be same.
        # Deterministic tie break on score descending, post_id ascending
        results = self.service.search("apple")
        self.assertEqual(results, ["t1", "t2", "t3"])

    def test_deletes_and_updates(self):
        self.service.upsert("u1", "unique term alpha")
        self.assertEqual(self.service.search("alpha"), ["u1"])
        
        self.service.delete("u1")
        self.assertEqual(self.service.search("alpha"), [])

        self.service.upsert("u2", "beta gamma")
        self.assertEqual(self.service.search("beta"), ["u2"])
        
        # update u2 to not have beta
        self.service.upsert("u2", "delta gamma")
        self.assertEqual(self.service.search("beta"), [])
        self.assertEqual(self.service.search("delta"), ["u2"])

if __name__ == "__main__":
    unittest.main()
