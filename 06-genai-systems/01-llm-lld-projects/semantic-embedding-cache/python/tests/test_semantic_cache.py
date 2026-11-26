import unittest
import importlib.util
import os

# Load semantic_cache.py dynamically
spec = importlib.util.spec_from_file_location(
    "semantic_cache", 
    os.path.join(os.path.dirname(__file__), "../v1-basic/semantic_cache.py")
)
semantic_cache_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(semantic_cache_module)

SemanticCache = semantic_cache_module.SemanticCache

class TestSemanticCache(unittest.TestCase):
    def setUp(self) -> None:
        self.max_capacity = 2
        self.sim_threshold = 0.90
        self.cache_instance = SemanticCache(capacity=self.max_capacity, tau=self.sim_threshold)
        self.tenant_a = "tenant_alpha"
        self.tenant_b = "tenant_beta"
        
        # Exact injected fixtures
        self.fixture_query_normal = "What is the capital of France?"
        self.fixture_embedding_normal = [1.0, 0.0]
        self.fixture_response_normal = "Paris"
        
        self.fixture_query_similar = "Tell me the capital of France"
        self.fixture_embedding_similar = [0.99, 0.14]
        
        self.fixture_query_dissimilar = "What is the capital of Germany?"
        self.fixture_embedding_dissimilar = [0.0, 1.0]
        
        self.fixture_embedding_error = [1.0, 0.0, 0.0]
        self.fixture_query_privacy = "What is the capital of France?"

    def test_normal_exact_match(self) -> None:
        self.cache_instance.put(
            self.tenant_a, 
            self.fixture_query_normal, 
            self.fixture_embedding_normal, 
            self.fixture_response_normal, 
            ttl_seconds=3600.0, 
            current_time=0.0
        )
        result = self.cache_instance.get(
            self.tenant_a, 
            self.fixture_query_normal, 
            self.fixture_embedding_normal, 
            current_time=1.0
        )
        self.assertEqual(result, self.fixture_response_normal)

    def test_normal_semantic_similarity_hit(self) -> None:
        self.cache_instance.put(
            self.tenant_a, 
            self.fixture_query_similar, 
            self.fixture_embedding_similar, 
            self.fixture_response_normal, 
            ttl_seconds=3600.0, 
            current_time=0.0
        )
        result = self.cache_instance.get(
            self.tenant_a, 
            self.fixture_query_normal, 
            self.fixture_embedding_normal, 
            current_time=1.0
        )
        self.assertEqual(result, self.fixture_response_normal)

    def test_normal_semantic_similarity_miss(self) -> None:
        self.cache_instance.put(
            self.tenant_a, 
            self.fixture_query_similar, 
            self.fixture_embedding_normal, 
            self.fixture_response_normal, 
            ttl_seconds=3600.0, 
            current_time=0.0
        )
        result = self.cache_instance.get(
            self.tenant_a, 
            self.fixture_query_dissimilar, 
            self.fixture_embedding_dissimilar, 
            current_time=1.0
        )
        self.assertIsNone(result)

    def test_normal_ttl_expiration(self) -> None:
        self.cache_instance.put(
            self.tenant_a, 
            self.fixture_query_normal, 
            self.fixture_embedding_normal, 
            self.fixture_response_normal, 
            ttl_seconds=10.0, 
            current_time=0.0
        )
        hit_before = self.cache_instance.get(
            self.tenant_a, 
            self.fixture_query_normal, 
            self.fixture_embedding_normal, 
            current_time=5.0
        )
        self.assertEqual(hit_before, self.fixture_response_normal)
        
        hit_after = self.cache_instance.get(
            self.tenant_a, 
            self.fixture_query_normal, 
            self.fixture_embedding_normal, 
            current_time=15.0
        )
        self.assertIsNone(hit_after)

    def test_normal_lru_eviction(self) -> None:
        self.cache_instance.put(self.tenant_a, "q1", [1.0, 0.0], "r1", ttl_seconds=100.0, current_time=0.0)
        self.cache_instance.put(self.tenant_a, "q2", [0.0, 1.0], "r2", ttl_seconds=100.0, current_time=1.0)
        self.cache_instance.put(self.tenant_a, "q3", [-1.0, 0.0], "r3", ttl_seconds=100.0, current_time=2.0)
        
        miss_q1 = self.cache_instance.get(self.tenant_a, "q1", [1.0, 0.0], current_time=3.0)
        self.assertIsNone(miss_q1)
        
        hit_q2 = self.cache_instance.get(self.tenant_a, "q2", [0.0, 1.0], current_time=3.0)
        self.assertEqual(hit_q2, "r2")
        
        hit_q3 = self.cache_instance.get(self.tenant_a, "q3", [-1.0, 0.0], current_time=3.0)
        self.assertEqual(hit_q3, "r3")

    def test_privacy_cross_tenant_isolation(self) -> None:
        self.cache_instance.put(
            self.tenant_a, 
            self.fixture_query_privacy, 
            self.fixture_embedding_normal, 
            self.fixture_response_normal, 
            ttl_seconds=3600.0, 
            current_time=0.0
        )
        hit_a = self.cache_instance.get(
            self.tenant_a, 
            self.fixture_query_privacy, 
            self.fixture_embedding_normal, 
            current_time=1.0
        )
        self.assertEqual(hit_a, self.fixture_response_normal)
        
        miss_b = self.cache_instance.get(
            self.tenant_b, 
            self.fixture_query_privacy, 
            self.fixture_embedding_normal, 
            current_time=1.0
        )
        self.assertIsNone(miss_b)

    def test_failure_mismatched_dimensions(self) -> None:
        self.cache_instance.put(
            self.tenant_a, 
            self.fixture_query_similar, 
            self.fixture_embedding_normal, 
            self.fixture_response_normal, 
            ttl_seconds=3600.0, 
            current_time=0.0
        )
        invalid_embedding = self.fixture_embedding_error
        with self.assertRaises(ValueError):
            self.cache_instance.get(self.tenant_a, self.fixture_query_normal, invalid_embedding, current_time=1.0)

    def test_failure_empty_input(self) -> None:
        with self.assertRaises(ValueError):
            self.cache_instance.put(self.tenant_a, "", self.fixture_embedding_normal, self.fixture_response_normal, ttl_seconds=3600.0, current_time=0.0)
            
        with self.assertRaises(ValueError):
            self.cache_instance.put(self.tenant_a, "valid_query", [], self.fixture_response_normal, ttl_seconds=3600.0, current_time=0.0)
            
        self.cache_instance.put(self.tenant_a, "valid_query", self.fixture_embedding_normal, self.fixture_response_normal, ttl_seconds=3600.0, current_time=0.0)
        
        with self.assertRaises(ValueError):
            self.cache_instance.get(self.tenant_a, "", self.fixture_embedding_normal, current_time=1.0)
            
        with self.assertRaises(ValueError):
            self.cache_instance.get(self.tenant_a, "valid_query", [], current_time=1.0)

    def test_cancellation_zero_ttl(self) -> None:
        self.cache_instance.put(
            self.tenant_a, 
            self.fixture_query_normal, 
            self.fixture_embedding_normal, 
            self.fixture_response_normal, 
            ttl_seconds=0.0, 
            current_time=0.0
        )
        result = self.cache_instance.get(
            self.tenant_a, 
            self.fixture_query_normal, 
            self.fixture_embedding_normal, 
            current_time=0.1
        )
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
