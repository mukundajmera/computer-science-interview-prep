import unittest
import threading
import importlib.util
import os

# Load semantic_cache_v2.py dynamically, mirroring test_semantic_cache.py's
# approach for the hyphenated version directories.
spec = importlib.util.spec_from_file_location(
    "semantic_cache_v2",
    os.path.join(os.path.dirname(__file__), "../v2-extended/semantic_cache_v2.py")
)
semantic_cache_v2_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(semantic_cache_v2_module)

SemanticCache = semantic_cache_v2_module.SemanticCache
EvictionPolicy = semantic_cache_v2_module.EvictionPolicy


class TestSemanticCacheV2ThreadSafety(unittest.TestCase):
    """v2 improvement: thread safety under concurrent access."""

    def test_concurrent_put_get_no_errors_and_bounded(self) -> None:
        cache = SemanticCache(capacity=10, tau=0.90)
        errors = []

        def worker(worker_id: int) -> None:
            try:
                for i in range(150):
                    # Short TTL forces the expiry scan to iterate while other
                    # threads mutate, the race v1 leaves unguarded.
                    cache.put("tenant_t", "q%d_%d" % (worker_id, i % 25),
                              [1.0, float(i % 3)], "resp", ttl_seconds=5.0,
                              current_time=float(i))
                    cache.get("tenant_t", "q%d_%d" % (worker_id, i % 25),
                              [1.0, float(i % 3)], current_time=float(i))
            except Exception as exc:  # pragma: no cover - failure path
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(w,)) for w in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [])
        tenant = cache.namespaces["tenant_t"]
        self.assertLessEqual(len(tenant.exact_cache), 10)

    def test_locking_disabled_still_functions(self) -> None:
        cache = SemanticCache(capacity=2, tau=0.90, enable_locking=False)
        cache.put("t", "hello", [1.0, 0.0], "world", ttl_seconds=10.0, current_time=0.0)
        self.assertEqual(cache.get("t", "hello", [1.0, 0.0], current_time=1.0), "world")


class TestSemanticCacheV2Metrics(unittest.TestCase):
    """v2 improvement: metrics counters and hooks."""

    def setUp(self) -> None:
        self.events = []

        def hook(event: str, tenant_id: str) -> None:
            self.events.append((event, tenant_id))

        self.hook = hook
        self.cache = SemanticCache(capacity=5, tau=0.90, metrics_hook=hook)

    def test_metrics_count_exact_hit_semantic_hit_and_miss(self) -> None:
        self.cache.put("t1", "What is the capital of France?", [1.0, 0.0], "Paris",
                       ttl_seconds=100.0, current_time=0.0)
        # Exact hit.
        self.cache.get("t1", "What is the capital of France?", [1.0, 0.0], current_time=1.0)
        # Semantic hit (similar, not identical query/embedding).
        self.cache.get("t1", "Tell me the capital of France", [0.99, 0.14], current_time=2.0)
        # Miss (dissimilar).
        self.cache.get("t1", "What is the capital of Germany?", [0.0, 1.0], current_time=3.0)

        snap = self.cache.metrics_snapshot()
        self.assertEqual(snap["exact_hit"], 1)
        self.assertEqual(snap["semantic_hit"], 1)
        self.assertEqual(snap["miss"], 1)

    def test_metrics_hook_receives_events_with_tenant(self) -> None:
        self.cache.put("tenant_hook", "q", [1.0, 0.0], "r",
                       ttl_seconds=100.0, current_time=0.0)
        self.cache.get("tenant_hook", "q", [1.0, 0.0], current_time=1.0)
        self.assertIn(("exact_hit", "tenant_hook"), self.events)

    def test_metrics_count_expiration_and_eviction(self) -> None:
        small = SemanticCache(capacity=1, tau=0.90)
        small.put("t", "q1", [1.0, 0.0], "r1", ttl_seconds=5.0, current_time=0.0)
        # Second put overflows capacity -> eviction of q1.
        small.put("t", "q2", [0.0, 1.0], "r2", ttl_seconds=100.0, current_time=1.0)
        # Third put after q2's would-be expiry forces the expiry path.
        small.put("t", "q3", [-1.0, 0.0], "r3", ttl_seconds=100.0, current_time=200.0)
        snap = small.metrics_snapshot()
        self.assertGreaterEqual(snap["evicted"], 1)
        self.assertGreaterEqual(snap["expired"], 1)

    def test_snapshot_is_a_copy(self) -> None:
        self.cache.put("t", "q", [1.0, 0.0], "r", ttl_seconds=10.0, current_time=0.0)
        snap = self.cache.metrics_snapshot()
        snap["miss"] = 999
        self.assertEqual(self.cache.metrics_snapshot()["miss"], 0)


class TestSemanticCacheV2EvictionPolicy(unittest.TestCase):
    """v2 improvement: configurable eviction policy."""

    def test_fifo_does_not_refresh_on_hit(self) -> None:
        cache = SemanticCache(capacity=2, tau=0.90,
                              eviction_policy=EvictionPolicy.FIFO)
        cache.put("t", "q1", [1.0, 0.0], "r1", ttl_seconds=100.0, current_time=0.0)
        cache.put("t", "q2", [0.0, 1.0], "r2", ttl_seconds=100.0, current_time=1.0)
        # Hit q1; under FIFO this must NOT protect q1 from eviction.
        self.assertEqual(cache.get("t", "q1", [1.0, 0.0], current_time=2.0), "r1")
        cache.put("t", "q3", [-1.0, 0.0], "r3", ttl_seconds=100.0, current_time=3.0)
        self.assertIsNone(cache.get("t", "q1", [1.0, 0.0], current_time=4.0))
        self.assertEqual(cache.get("t", "q2", [0.0, 1.0], current_time=4.0), "r2")

    def test_lru_default_refreshes_on_hit(self) -> None:
        cache = SemanticCache(capacity=2, tau=0.90)  # default is LRU
        cache.put("t", "q1", [1.0, 0.0], "r1", ttl_seconds=100.0, current_time=0.0)
        cache.put("t", "q2", [0.0, 1.0], "r2", ttl_seconds=100.0, current_time=1.0)
        # Hit q1; under LRU q2 (not q1) becomes the eviction victim.
        self.assertEqual(cache.get("t", "q1", [1.0, 0.0], current_time=2.0), "r1")
        cache.put("t", "q3", [-1.0, 0.0], "r3", ttl_seconds=100.0, current_time=3.0)
        self.assertEqual(cache.get("t", "q1", [1.0, 0.0], current_time=4.0), "r1")
        self.assertIsNone(cache.get("t", "q2", [0.0, 1.0], current_time=4.0))


class TestSemanticCacheV2ConfigVersioning(unittest.TestCase):
    """v2 improvement: config (system-prompt) versioning and invalidation."""

    def test_version_bump_invalidates_exact_match(self) -> None:
        cache = SemanticCache(capacity=10, tau=0.90)
        cache.put("t", "What is the capital of France?", [1.0, 0.0], "Paris (persona A)",
                  ttl_seconds=1000.0, current_time=0.0)
        invalidated = cache.set_config_version("t", "persona-b")
        self.assertEqual(invalidated, 1)
        # Same exact query must now miss: the persona-A answer is stale.
        self.assertIsNone(
            cache.get("t", "What is the capital of France?", [1.0, 0.0], current_time=1.0)
        )

    def test_version_bump_invalidates_semantic_match(self) -> None:
        cache = SemanticCache(capacity=10, tau=0.90)
        cache.put("t", "q", [1.0, 0.0], "old answer", ttl_seconds=1000.0, current_time=0.0)
        cache.set_config_version("t", "v2")
        # A semantically identical query must not resurrect the stale entry.
        self.assertIsNone(cache.get("t", "q rephrased", [0.99, 0.14], current_time=1.0))

    def test_new_entries_use_new_version(self) -> None:
        cache = SemanticCache(capacity=10, tau=0.90)
        cache.put("t", "q", [1.0, 0.0], "old", ttl_seconds=1000.0, current_time=0.0)
        cache.set_config_version("t", "v2")
        cache.put("t", "q", [1.0, 0.0], "new", ttl_seconds=1000.0, current_time=1.0)
        self.assertEqual(cache.get("t", "q", [1.0, 0.0], current_time=2.0), "new")
        snap = cache.metrics_snapshot()
        self.assertEqual(snap["invalidated"], 1)

    def test_version_bump_is_tenant_scoped(self) -> None:
        cache = SemanticCache(capacity=10, tau=0.90)
        cache.put("ta", "q", [1.0, 0.0], "ra", ttl_seconds=1000.0, current_time=0.0)
        cache.put("tb", "q", [1.0, 0.0], "rb", ttl_seconds=1000.0, current_time=0.0)
        cache.set_config_version("ta", "v2")
        self.assertIsNone(cache.get("ta", "q", [1.0, 0.0], current_time=1.0))
        self.assertEqual(cache.get("tb", "q", [1.0, 0.0], current_time=1.0), "rb")


class TestSemanticCacheV2ValidationAndEdges(unittest.TestCase):
    """v2 validation improvements and edge cases."""

    def test_dimension_mismatch_at_put_raises(self) -> None:
        cache = SemanticCache(capacity=5, tau=0.90)
        cache.put("t", "q1", [1.0, 0.0], "r1", ttl_seconds=100.0, current_time=0.0)
        with self.assertRaises(ValueError):
            cache.put("t", "q2", [1.0, 0.0, 0.0], "r2", ttl_seconds=100.0, current_time=1.0)

    def test_dimension_mismatch_at_get_raises(self) -> None:
        cache = SemanticCache(capacity=5, tau=0.90)
        cache.put("t", "q1", [1.0, 0.0], "r1", ttl_seconds=100.0, current_time=0.0)
        with self.assertRaises(ValueError):
            cache.get("t", "q1", [1.0, 0.0, 0.0], current_time=1.0)

    def test_empty_tenant_id_raises(self) -> None:
        cache = SemanticCache(capacity=5, tau=0.90)
        with self.assertRaises(ValueError):
            cache.put("", "q", [1.0, 0.0], "r", ttl_seconds=100.0, current_time=0.0)
        with self.assertRaises(ValueError):
            cache.get("", "q", [1.0, 0.0], current_time=0.0)

    def test_constructor_validation(self) -> None:
        with self.assertRaises(ValueError):
            SemanticCache(capacity=0)
        with self.assertRaises(ValueError):
            SemanticCache(tau=0.0)
        with self.assertRaises(ValueError):
            SemanticCache(tau=1.5)
        with self.assertRaises(ValueError):
            SemanticCache().set_config_version("t", "")

    def test_unknown_tenant_get_counts_miss(self) -> None:
        cache = SemanticCache(capacity=5, tau=0.90)
        self.assertIsNone(cache.get("ghost", "q", [1.0, 0.0], current_time=0.0))
        self.assertEqual(cache.metrics_snapshot()["miss"], 1)

    def test_v1_behaviour_parity_ttl_zero_and_isolation(self) -> None:
        cache = SemanticCache(capacity=5, tau=0.90)
        cache.put("ta", "q", [1.0, 0.0], "r", ttl_seconds=0.0, current_time=0.0)
        self.assertIsNone(cache.get("ta", "q", [1.0, 0.0], current_time=0.1))
        cache.put("ta", "q", [1.0, 0.0], "r", ttl_seconds=100.0, current_time=1.0)
        self.assertIsNone(cache.get("tb", "q", [1.0, 0.0], current_time=2.0))


if __name__ == "__main__":
    unittest.main()
