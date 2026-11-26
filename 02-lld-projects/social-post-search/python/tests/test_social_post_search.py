import os
import sys
import unittest

BASE_DIR = os.path.dirname(__file__)
V1_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v1-basic"))
if V1_DIR not in sys.path:
    sys.path.insert(0, V1_DIR)

from post_ingestion_service import PostIngestionService


class PostIngestionServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = PostIngestionService()
        self.service.ingest_post("p1", "The quick brown fox jumps over the lazy dog.")
        self.service.ingest_post("p2", "A fast brown fox leaps across a sleeping dog.")
        self.service.ingest_post("p3", "Dogs are great companions for a walk in the park.")
        self.service.ingest_post("p4", "Fox fox fox! Look at that fast brown fox!")

    def test_tokenization_and_filtering(self):
        tokens = self.service._tokenize_and_filter("The quick brown Fox in a box")
        self.assertEqual(tokens, ["quick", "brown", "fox", "box"])
        # Stop words 'the', 'in', 'a' are removed, and lowercase is applied

    def test_boolean_and_search(self):
        # Should match p1 and p2 (both have "brown" and "fox")
        results = self.service.search_and("brown fox")
        self.assertEqual(set(results), {"p1", "p2", "p4"})
        
        # Should only match p1
        results_lazy = self.service.search_and("lazy dog")
        self.assertEqual(results_lazy, ["p1"])
        
        # Should not match any
        results_none = self.service.search_and("fox elephant")
        self.assertEqual(results_none, [])

    def test_boolean_or_search(self):
        # Should match p1, p2, p3, p4
        results = self.service.search_or("lazy companions")
        self.assertEqual(set(results), {"p1", "p3"})
        
        results_fox = self.service.search_or("fox")
        self.assertEqual(set(results_fox), {"p1", "p2", "p4"})

    def test_relevance_ranking(self):
        # p4 has "fox" 4 times, "brown" 1 time (score = 5)
        # p1 has "fox" 1 time, "brown" 1 time (score = 2)
        # p2 has "fox" 1 time, "brown" 1 time (score = 2)
        results = self.service.search_or("brown fox")
        
        self.assertEqual(results[0], "p4")
        self.assertTrue(results[1] in ["p1", "p2"] or results[2] in ["p1", "p2"])

if __name__ == "__main__":
    unittest.main()
