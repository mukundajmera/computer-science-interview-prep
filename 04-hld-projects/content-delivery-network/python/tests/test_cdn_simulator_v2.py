import unittest
import sys
import os

# Add the parent directory to the path so we can import v2-extended
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from importlib import import_module
cdn_simulator = import_module('v2-extended.cdn_simulator')

CustomerOrigin = cdn_simulator.CustomerOrigin
OriginShield = cdn_simulator.OriginShield
EdgeNode = cdn_simulator.EdgeNode
OriginError = cdn_simulator.OriginError
normalize_key = cdn_simulator.normalize_key


class FakeClock:
    def __init__(self, now=1000.0):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def build(clock=None, **edge_kwargs):
    origin = CustomerOrigin()
    shield = OriginShield(origin)
    edge = EdgeNode(shield, clock=clock, **edge_kwargs)
    return origin, shield, edge


class TestCdnSimulatorV2(unittest.TestCase):

    # --- v1 parity -----------------------------------------------------------

    def test_normal_hit(self):
        origin, shield, edge = build()
        origin.put("/images/logo.png", "binary_data_123")

        result1 = edge.fetch("/images/logo.png")
        self.assertEqual(result1, "binary_data_123")
        self.assertEqual(origin.fetch_count, 1)

        result2 = edge.fetch("/images/logo.png")
        self.assertEqual(result2, "binary_data_123")
        self.assertEqual(edge.cache_hit_count, 1)
        self.assertEqual(origin.fetch_count, 1)  # Origin not hit again

    def test_thundering_herd_coalescing(self):
        origin, shield, edge = build()
        origin.put("/videos/viral.mp4", "video_data_999")

        results = []
        edge.fetch_batch("/videos/viral.mp4", 10000, results)

        self.assertEqual(len(results), 10000)
        for res in results:
            self.assertEqual(res, "video_data_999")
        self.assertEqual(origin.fetch_count, 1)
        self.assertEqual(shield.fetch_count, 10000)

    # --- v2 item 1: cache-key normalization ----------------------------------

    def test_random_query_busters_share_one_cache_entry(self):
        origin, shield, edge = build()
        origin.put("/a", "data-a")

        self.assertEqual(edge.fetch("/a?cb=123"), "data-a")
        self.assertEqual(edge.fetch("/a?cb=456"), "data-a")
        # The second fetch was an edge hit: the random buster did not bypass.
        self.assertEqual(origin.fetch_count, 1)
        self.assertEqual(edge.cache_hit_count, 1)

    def test_all_params_stripped_without_whitelist(self):
        key1 = normalize_key("/a?x=1&y=2")
        key2 = normalize_key("/a")
        self.assertEqual(key1, key2)
        self.assertEqual(key1, "default:/a")

    def test_whitelisted_params_distinguish_entries_sorted(self):
        origin, shield, edge = build()
        origin.put("/a?v=1", "data-v1")
        origin.put("/a?v=2", "data-v2")

        self.assertEqual(
            edge.fetch("/a?v=1&cb=x", allowed_params={"v"}), "data-v1")
        self.assertEqual(
            edge.fetch("/a?v=2&cb=y", allowed_params={"v"}), "data-v2")
        self.assertEqual(origin.fetch_count, 2)  # distinct whitelisted keys
        # Sorted param order makes /a?v=1 and /a?cb=z&v=1 equivalent.
        self.assertEqual(
            edge.fetch("/a?cb=z&v=1", allowed_params={"v"}), "data-v1")
        self.assertEqual(origin.fetch_count, 2)

    def test_customer_id_separates_cache_keys(self):
        origin, shield, edge = build()
        origin.put("/a", "data-a")

        edge.fetch("/a", customer_id="cust-1")
        edge.fetch("/a", customer_id="cust-2")
        # Two distinct edge entries were filled through the shield; the shield
        # is shared across tenants, so the origin was hit only once.
        self.assertEqual(origin.fetch_count, 1)
        self.assertEqual(shield.fetch_count, 2)
        self.assertIn("cust-1:/a", edge.cache)
        self.assertIn("cust-2:/a", edge.cache)

    # --- v2 item 2: TTL expiry + stale-on-error ------------------------------

    def test_ttl_expiry_triggers_revalidation(self):
        clock = FakeClock()
        origin, shield, edge = build(clock=clock, ttl=10.0)
        origin.put("/a", "data-a")

        edge.fetch("/a")
        self.assertEqual(origin.fetch_count, 1)
        clock.advance(11.0)
        # The shield still caches, so revalidation does not reach the origin.
        edge.fetch("/a")
        self.assertEqual(edge.stale_served_count, 0)

    def test_stale_on_error_serves_expired_entry(self):
        clock = FakeClock()
        origin, shield, edge = build(clock=clock, ttl=10.0, stale_window=100.0)
        origin.put("/a", "data-a")

        edge.fetch("/a")
        shield.cache.clear()  # force the next revalidation to reach the origin
        origin.fail = True
        clock.advance(11.0)  # past ttl, inside stale window
        self.assertEqual(edge.fetch("/a"), "data-a")
        self.assertEqual(edge.stale_served_count, 1)

    def test_beyond_stale_window_propagates_origin_error(self):
        clock = FakeClock()
        origin, shield, edge = build(clock=clock, ttl=10.0, stale_window=100.0)
        origin.put("/a", "data-a")

        edge.fetch("/a")
        shield.cache.clear()
        origin.fail = True
        clock.advance(111.0)  # past ttl + stale_window
        with self.assertRaises(OriginError):
            edge.fetch("/a")

    def test_origin_error_without_entry_propagates(self):
        origin, shield, edge = build()
        origin.fail = True
        with self.assertRaises(OriginError):
            edge.fetch("/missing")

    def test_origin_error_releases_in_flight_marker(self):
        origin, shield, edge = build()
        origin.put("/a", "data-a")

        origin.fail = True
        with self.assertRaises(OriginError):
            shield.fetch("/a")
        origin.fail = False
        # If the marker leaked, this fetch would return "COALESCED" forever.
        self.assertEqual(shield.fetch("/a"), "data-a")

    # --- v2 item 3: bounded LRU eviction -------------------------------------

    def test_lru_eviction_bounds_cache_size(self):
        origin, shield, edge = build(max_entries=2)
        for name in ("/a", "/b", "/c"):
            origin.put(name, "data" + name)
            edge.fetch(name)

        self.assertEqual(len(edge.cache), 2)
        self.assertNotIn("default:/a", edge.cache)  # oldest evicted
        edge.fetch("/a")
        # The eviction forced a shield round-trip; the shared shield cache
        # still protects the origin, which stays at 3 fetches.
        self.assertEqual(shield.fetch_count, 4)
        self.assertEqual(origin.fetch_count, 3)

    def test_fresh_hit_refreshes_lru_recency(self):
        origin, shield, edge = build(max_entries=2)
        for name in ("/a", "/b"):
            origin.put(name, "data" + name)
        edge.fetch("/a")
        edge.fetch("/b")
        edge.fetch("/a")  # hit: /a becomes most-recently-used
        origin.put("/c", "data/c")
        edge.fetch("/c")

        self.assertIn("default:/a", edge.cache)
        self.assertNotIn("default:/b", edge.cache)  # /b evicted instead

    # --- edges ----------------------------------------------------------------

    def test_purge_uses_normalized_key(self):
        origin, shield, edge = build()
        origin.put("/a", "data-a")
        edge.fetch("/a?cb=1")
        edge.purge("/a?cb=2")  # same normalized entry
        edge.fetch("/a")
        # The purge really removed the edge entry: the request went back to
        # the shield (fetch 2), which served it without touching the origin.
        self.assertEqual(shield.fetch_count, 2)
        self.assertEqual(origin.fetch_count, 1)

    def test_invalid_policy_values_rejected(self):
        origin, shield, _ = build()
        with self.assertRaises(ValueError):
            EdgeNode(shield, ttl=-1.0)
        with self.assertRaises(ValueError):
            EdgeNode(shield, stale_window=-1.0)
        with self.assertRaises(ValueError):
            EdgeNode(shield, max_entries=0)


if __name__ == '__main__':
    unittest.main()
