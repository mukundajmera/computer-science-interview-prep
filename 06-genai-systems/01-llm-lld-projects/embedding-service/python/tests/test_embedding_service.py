"""
Tests for Embedding Service (v1-basic).
"""
import unittest
import sys
import os
import math
import time

# Add v1-basic to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))


class TestRandomEmbeddingModel(unittest.TestCase):
    """Tests for RandomEmbeddingModel."""

    def setUp(self):
        from embedding_model import RandomEmbeddingModel
        self.RandomEmbeddingModel = RandomEmbeddingModel

    def test_output_dimensions(self):
        """Output vector should have the configured number of dimensions."""
        model = self.RandomEmbeddingModel(dimensions=64)
        embedding = model.embed("hello")
        self.assertEqual(len(embedding), 64)

    def test_model_name(self):
        """Model name should be 'random'."""
        model = self.RandomEmbeddingModel()
        self.assertEqual(model.model_name, "random")

    def test_dimensions_property(self):
        """Dimensions property should match constructor argument."""
        model = self.RandomEmbeddingModel(dimensions=32)
        self.assertEqual(model.dimensions, 32)

    def test_values_in_range(self):
        """All values should be in [0, 1)."""
        model = self.RandomEmbeddingModel(dimensions=100)
        embedding = model.embed("test")
        for v in embedding:
            self.assertGreaterEqual(v, 0.0)
            self.assertLess(v, 1.0)

    def test_non_deterministic(self):
        """Different calls should generally produce different vectors."""
        model = self.RandomEmbeddingModel(dimensions=128)
        e1 = model.embed("same text")
        e2 = model.embed("same text")
        # Extremely unlikely to be identical
        self.assertNotEqual(e1, e2)

    def test_embed_batch(self):
        """Batch embedding should return one vector per input text."""
        model = self.RandomEmbeddingModel(dimensions=16)
        results = model.embed_batch(["a", "b", "c"])
        self.assertEqual(len(results), 3)
        for vec in results:
            self.assertEqual(len(vec), 16)

    def test_invalid_dimensions_raises(self):
        """Zero or negative dimensions should raise ValueError."""
        with self.assertRaises(ValueError):
            self.RandomEmbeddingModel(dimensions=0)
        with self.assertRaises(ValueError):
            self.RandomEmbeddingModel(dimensions=-5)


class TestHashEmbeddingModel(unittest.TestCase):
    """Tests for HashEmbeddingModel."""

    def setUp(self):
        from embedding_model import HashEmbeddingModel
        self.HashEmbeddingModel = HashEmbeddingModel

    def test_output_dimensions(self):
        """Output vector should have the configured number of dimensions."""
        model = self.HashEmbeddingModel(dimensions=64)
        embedding = model.embed("hello")
        self.assertEqual(len(embedding), 64)

    def test_model_name(self):
        """Model name should be 'hash'."""
        model = self.HashEmbeddingModel()
        self.assertEqual(model.model_name, "hash")

    def test_deterministic(self):
        """Same text should always produce the same embedding."""
        model = self.HashEmbeddingModel(dimensions=128)
        e1 = model.embed("deterministic test")
        e2 = model.embed("deterministic test")
        self.assertEqual(e1, e2)

    def test_different_texts_differ(self):
        """Different texts should produce different embeddings."""
        model = self.HashEmbeddingModel(dimensions=128)
        e1 = model.embed("hello")
        e2 = model.embed("world")
        self.assertNotEqual(e1, e2)

    def test_values_in_range(self):
        """All values should be in [0, 1]."""
        model = self.HashEmbeddingModel(dimensions=100)
        embedding = model.embed("range test")
        for v in embedding:
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0)

    def test_embed_batch_deterministic(self):
        """Batch embedding should be deterministic and correctly sized."""
        model = self.HashEmbeddingModel(dimensions=16)
        results = model.embed_batch(["a", "b"])
        self.assertEqual(len(results), 2)
        # Verify determinism
        results2 = model.embed_batch(["a", "b"])
        self.assertEqual(results, results2)

    def test_invalid_dimensions_raises(self):
        """Zero or negative dimensions should raise ValueError."""
        with self.assertRaises(ValueError):
            self.HashEmbeddingModel(dimensions=0)


class TestEmbeddingCache(unittest.TestCase):
    """Tests for EmbeddingCache."""

    def setUp(self):
        from cache import EmbeddingCache
        self.EmbeddingCache = EmbeddingCache

    def test_put_and_get(self):
        """Stored embedding should be retrievable by key."""
        cache = self.EmbeddingCache(max_size=10, ttl_seconds=60)
        cache.put("key1", [1.0, 2.0, 3.0])
        result = cache.get("key1")
        self.assertEqual(result, [1.0, 2.0, 3.0])

    def test_miss_returns_none(self):
        """Getting a non-existent key should return None."""
        cache = self.EmbeddingCache()
        self.assertIsNone(cache.get("nonexistent"))

    def test_ttl_expiry(self):
        """Entries older than TTL should be treated as misses."""
        cache = self.EmbeddingCache(max_size=10, ttl_seconds=0.1)
        cache.put("key1", [1.0])
        time.sleep(0.2)
        result = cache.get("key1")
        self.assertIsNone(result)

    def test_ttl_not_expired(self):
        """Entries within TTL should be retrievable."""
        cache = self.EmbeddingCache(max_size=10, ttl_seconds=10)
        cache.put("key1", [1.0])
        result = cache.get("key1")
        self.assertEqual(result, [1.0])

    def test_max_size_eviction(self):
        """When max_size is reached, oldest entry should be evicted."""
        cache = self.EmbeddingCache(max_size=2, ttl_seconds=60)
        cache.put("k1", [1.0])
        cache.put("k2", [2.0])
        cache.put("k3", [3.0])  # Should evict k1
        self.assertIsNone(cache.get("k1"))
        self.assertEqual(cache.get("k2"), [2.0])
        self.assertEqual(cache.get("k3"), [3.0])

    def test_overwrite_existing_key(self):
        """Overwriting an existing key should update the value."""
        cache = self.EmbeddingCache(max_size=10, ttl_seconds=60)
        cache.put("key1", [1.0])
        cache.put("key1", [2.0])
        self.assertEqual(cache.get("key1"), [2.0])
        self.assertEqual(cache.size, 1)

    def test_stats_hits_and_misses(self):
        """Stats should accurately track hits and misses."""
        cache = self.EmbeddingCache(max_size=10, ttl_seconds=60)
        cache.put("key1", [1.0])
        cache.get("key1")   # hit
        cache.get("key1")   # hit
        cache.get("miss")   # miss
        stats = cache.stats()
        self.assertEqual(stats["hits"], 2)
        self.assertEqual(stats["misses"], 1)
        self.assertAlmostEqual(stats["hit_rate"], 2 / 3)

    def test_hit_rate_no_lookups(self):
        """Hit rate should be 0.0 when no lookups have been made."""
        cache = self.EmbeddingCache()
        self.assertEqual(cache.hit_rate, 0.0)

    def test_clear_resets_everything(self):
        """Clear should remove all entries and reset counters."""
        cache = self.EmbeddingCache(max_size=10, ttl_seconds=60)
        cache.put("k1", [1.0])
        cache.get("k1")
        cache.clear()
        self.assertEqual(cache.size, 0)
        self.assertIsNone(cache.get("k1"))
        stats = cache.stats()
        # After clear, the get("k1") above adds 1 miss
        self.assertEqual(stats["hits"], 0)
        self.assertEqual(stats["misses"], 1)

    def test_size_property(self):
        """Size property should reflect the number of stored entries."""
        cache = self.EmbeddingCache(max_size=10, ttl_seconds=60)
        self.assertEqual(cache.size, 0)
        cache.put("k1", [1.0])
        self.assertEqual(cache.size, 1)
        cache.put("k2", [2.0])
        self.assertEqual(cache.size, 2)

    def test_max_size_zero_stores_nothing(self):
        """A cache with max_size=0 should never store entries."""
        cache = self.EmbeddingCache(max_size=0, ttl_seconds=60)
        cache.put("k1", [1.0])
        self.assertEqual(cache.size, 0)
        self.assertIsNone(cache.get("k1"))


class TestEmbeddingService(unittest.TestCase):
    """Tests for EmbeddingService."""

    def setUp(self):
        from embedding_model import HashEmbeddingModel
        from cache import EmbeddingCache
        from service import EmbeddingService
        self.HashEmbeddingModel = HashEmbeddingModel
        self.EmbeddingCache = EmbeddingCache
        self.EmbeddingService = EmbeddingService

        self.model = HashEmbeddingModel(dimensions=16)
        self.cache = EmbeddingCache(max_size=100, ttl_seconds=60)
        self.service = EmbeddingService(model=self.model, cache=self.cache)

    def test_embed_returns_result(self):
        """Embed should return an EmbeddingResult with correct fields."""
        result = self.service.embed("hello world")
        self.assertEqual(result.text, "hello world")
        self.assertEqual(result.model_name, "hash")
        self.assertEqual(result.dimensions, 16)
        self.assertEqual(len(result.embedding), 16)
        self.assertFalse(result.cached)

    def test_embed_cache_hit(self):
        """Second call with same text should return a cached result."""
        r1 = self.service.embed("cached text")
        r2 = self.service.embed("cached text")
        self.assertFalse(r1.cached)
        self.assertTrue(r2.cached)
        self.assertEqual(r1.embedding, r2.embedding)

    def test_embed_without_cache(self):
        """Service without cache should still work."""
        service = self.EmbeddingService(model=self.model, cache=None)
        result = service.embed("no cache")
        self.assertFalse(result.cached)
        self.assertEqual(len(result.embedding), 16)

    def test_embed_batch(self):
        """Batch embed should return one result per input text."""
        results = self.service.embed_batch(["a", "b", "c"])
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertEqual(r.dimensions, 16)

    def test_embed_batch_caching(self):
        """Batch embed with duplicates should hit cache for repeated texts."""
        results = self.service.embed_batch(["dup", "dup"])
        self.assertFalse(results[0].cached)
        self.assertTrue(results[1].cached)

    def test_normalization(self):
        """Output embeddings should be L2-normalised to unit length."""
        result = self.service.embed("normalize me")
        magnitude = math.sqrt(sum(x * x for x in result.embedding))
        self.assertAlmostEqual(magnitude, 1.0, places=6)

    def test_normalize_zero_vector(self):
        """Normalizing a zero vector should return the zero vector."""
        normalized = self.EmbeddingService.normalize_embedding([0.0, 0.0, 0.0])
        self.assertEqual(normalized, [0.0, 0.0, 0.0])

    def test_normalize_unit_vector(self):
        """Normalizing a unit vector should return approximately the same vector."""
        normalized = self.EmbeddingService.normalize_embedding([1.0, 0.0, 0.0])
        self.assertAlmostEqual(normalized[0], 1.0, places=6)
        self.assertAlmostEqual(normalized[1], 0.0, places=6)
        self.assertAlmostEqual(normalized[2], 0.0, places=6)

    def test_get_stats(self):
        """Stats should include model info, total embeddings, and cache stats."""
        self.service.embed("stat test")
        stats = self.service.get_stats()
        self.assertEqual(stats["model"], "hash")
        self.assertEqual(stats["dimensions"], 16)
        self.assertEqual(stats["total_embeddings"], 1)
        self.assertIn("cache", stats)
        self.assertIn("hits", stats["cache"])
        self.assertIn("misses", stats["cache"])

    def test_get_stats_no_cache(self):
        """Stats without cache should omit the cache section."""
        service = self.EmbeddingService(model=self.model, cache=None)
        stats = service.get_stats()
        self.assertNotIn("cache", stats)

    def test_empty_string_raises(self):
        """Embedding an empty string should raise ValueError."""
        with self.assertRaises(ValueError):
            self.service.embed("")

    def test_whitespace_only_raises(self):
        """Embedding a whitespace-only string should raise ValueError."""
        with self.assertRaises(ValueError):
            self.service.embed("   \t\n  ")

    def test_batch_empty_string_raises(self):
        """Batch embed with an empty string should raise ValueError."""
        with self.assertRaises(ValueError):
            self.service.embed_batch(["valid", ""])

    def test_very_long_text(self):
        """Very long text should be accepted and produce correct dimensions."""
        long_text = "word " * 10000
        result = self.service.embed(long_text)
        self.assertEqual(len(result.embedding), 16)

    def test_unicode_text(self):
        """Unicode text should be accepted and produce correct dimensions."""
        result = self.service.embed("こんにちは世界 🌍")
        self.assertEqual(len(result.embedding), 16)

    def test_total_embeddings_counter(self):
        """Total embeddings counter should increment for each call."""
        self.service.embed("one")
        self.service.embed("two")
        self.service.embed("one")  # cache hit still counts
        stats = self.service.get_stats()
        self.assertEqual(stats["total_embeddings"], 3)


class TestEmbeddingServiceDeterminism(unittest.TestCase):
    """Tests verifying deterministic behaviour with HashEmbeddingModel."""

    def setUp(self):
        from embedding_model import HashEmbeddingModel
        from service import EmbeddingService
        self.model = HashEmbeddingModel(dimensions=32)
        self.service = EmbeddingService(model=self.model, cache=None)

    def test_same_text_same_embedding(self):
        """Same text should produce identical embeddings across calls."""
        r1 = self.service.embed("repeatable")
        r2 = self.service.embed("repeatable")
        self.assertEqual(r1.embedding, r2.embedding)

    def test_different_text_different_embedding(self):
        """Different texts should produce different embeddings."""
        r1 = self.service.embed("alpha")
        r2 = self.service.embed("beta")
        self.assertNotEqual(r1.embedding, r2.embedding)


if __name__ == "__main__":
    unittest.main()
