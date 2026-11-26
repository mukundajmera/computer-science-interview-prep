"""Tests for CDN implementations."""

import unittest
import time
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-realistic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-production'))


class TestSimpleProxyCache(unittest.TestCase):
    """Tests for SimpleProxyCache."""
    
    def test_cache_hit(self):
        """Should return cached content on second request."""
        from simple_proxy_cache import SimpleProxyCache
        
        fetch_count = [0]
        def origin(url):
            fetch_count[0] += 1
            return f"content-{url}"
        
        cache = SimpleProxyCache(origin, default_ttl_seconds=60)
        
        result1 = cache.fetch("/test.html")
        result2 = cache.fetch("/test.html")
        
        self.assertEqual(result1, result2)
        self.assertEqual(fetch_count[0], 1)  # Only one origin fetch
    
    def test_cache_miss(self):
        """Should fetch from origin on cache miss."""
        from simple_proxy_cache import SimpleProxyCache
        
        fetch_count = [0]
        def origin(url):
            fetch_count[0] += 1
            return f"content-{url}"
        
        cache = SimpleProxyCache(origin, default_ttl_seconds=60)
        
        cache.fetch("/page1.html")
        cache.fetch("/page2.html")
        
        self.assertEqual(fetch_count[0], 2)  # Two different URLs
    
    def test_purge(self):
        """Should remove content on purge."""
        from simple_proxy_cache import SimpleProxyCache
        
        fetch_count = [0]
        def origin(url):
            fetch_count[0] += 1
            return f"content-{fetch_count[0]}"
        
        cache = SimpleProxyCache(origin, default_ttl_seconds=60)
        
        cache.fetch("/test.html")
        cache.purge("/test.html")
        result = cache.fetch("/test.html")
        
        self.assertEqual(result, "content-2")
        self.assertEqual(fetch_count[0], 2)
    
    def test_hit_rate(self):
        """Should track hit rate correctly."""
        from simple_proxy_cache import SimpleProxyCache
        
        cache = SimpleProxyCache(lambda url: "content", default_ttl_seconds=60)
        
        cache.fetch("/a")  # miss
        cache.fetch("/a")  # hit
        cache.fetch("/a")  # hit
        cache.fetch("/b")  # miss
        
        self.assertAlmostEqual(cache.hit_rate, 50.0, places=1)


class TestGeographicCDN(unittest.TestCase):
    """Tests for GeographicCDN."""
    
    def test_geographic_routing(self):
        """Should route users to correct edge."""
        from geographic_cdn import GeographicCDN
        
        cdn = GeographicCDN(lambda url: "content", 60, 30)
        
        edge_japan = cdn.route_to_edge("japan")
        edge_germany = cdn.route_to_edge("germany")
        edge_california = cdn.route_to_edge("california")
        
        self.assertEqual(edge_japan.name, "asia-east")
        self.assertEqual(edge_germany.name, "eu-west")
        self.assertEqual(edge_california.name, "us-west")
    
    def test_shield_caching(self):
        """Shield should cache for all edges."""
        from geographic_cdn import GeographicCDN
        
        origin_calls = [0]
        def origin(url):
            origin_calls[0] += 1
            return f"content-{origin_calls[0]}"
        
        cdn = GeographicCDN(origin, 60, 30)
        
        # First region fetches from origin
        cdn.fetch("japan", "/video.mp4")
        # Second region gets from shield
        cdn.fetch("germany", "/video.mp4")
        
        # Only one origin call (shield cached it)
        self.assertEqual(origin_calls[0], 1)
    
    def test_global_purge(self):
        """Should purge from all edges."""
        from geographic_cdn import GeographicCDN
        
        origin_calls = [0]
        def origin(url):
            origin_calls[0] += 1
            return f"content-{origin_calls[0]}"
        
        cdn = GeographicCDN(origin, 60, 30)
        
        cdn.fetch("japan", "/video.mp4")
        cdn.fetch("germany", "/video.mp4")
        
        cdn.purge_global("/video.mp4")
        
        # After purge, should fetch from origin again
        cdn.fetch("japan", "/video.mp4")
        
        self.assertEqual(origin_calls[0], 2)


class TestProductionCDN(unittest.TestCase):
    """Tests for ProductionCDN."""
    
    def test_cache_control_parsing(self):
        """Should parse Cache-Control headers."""
        from production_cdn import CacheControl
        
        cc = CacheControl.parse("max-age=300, stale-while-revalidate=60")
        
        self.assertEqual(cc.max_age_seconds, 300)
        self.assertEqual(cc.stale_while_revalidate_seconds, 60)
        self.assertFalse(cc.no_cache)
    
    def test_no_cache_directive(self):
        """Should bypass cache with no-cache."""
        from production_cdn import ProductionCDN
        
        fetch_count = [0]
        def origin(url):
            fetch_count[0] += 1
            return f"content-{fetch_count[0]}"
        
        cdn = ProductionCDN(origin)
        
        cdn.fetch("japan", "/api/data", {})
        cdn.fetch("japan", "/api/data", {"Cache-Control": "no-cache"})
        
        self.assertEqual(fetch_count[0], 2)
        cdn.shutdown()
    
    def test_purge_wildcard(self):
        """Should purge matching patterns."""
        from production_cdn import ProductionCDN
        
        cdn = ProductionCDN(lambda url: "content")
        
        cdn.fetch("japan", "/images/a.jpg", {})
        cdn.fetch("japan", "/images/b.jpg", {})
        cdn.fetch("japan", "/videos/c.mp4", {})
        
        cdn.purge("/images/*").result()
        
        # Images should be purged, video should still be cached
        r1 = cdn.fetch("japan", "/images/a.jpg", {})
        r2 = cdn.fetch("japan", "/videos/c.mp4", {})
        
        self.assertFalse(r1.cache_hit)  # Purged
        self.assertTrue(r2.cache_hit)   # Still cached
        
        cdn.shutdown()
    
    def test_metrics_tracking(self):
        """Should track metrics correctly."""
        from production_cdn import ProductionCDN
        
        cdn = ProductionCDN(lambda url: "content")
        
        cdn.fetch("japan", "/a", {})  # miss
        cdn.fetch("japan", "/a", {})  # hit
        cdn.fetch("japan", "/b", {})  # miss
        
        self.assertGreater(cdn.metrics.hit_rate, 30)
        self.assertLess(cdn.metrics.hit_rate, 40)
        
        cdn.shutdown()

    def test_metrics_zero_requests(self):
        """Should handle zero requests without errors (division by zero)."""
        from production_cdn import ProductionCDN
        
        cdn = ProductionCDN(lambda url: "content")
        
        self.assertEqual(cdn.metrics.hit_rate, 0.0)
        self.assertEqual(cdn.metrics.average_latency_ms, 0.0)
        
        cdn.shutdown()

    def test_metrics_purge_tracking(self):
        """Should track purges correctly in metrics."""
        from production_cdn import ProductionCDN
        
        cdn = ProductionCDN(lambda url: "content")
        
        cdn.fetch("japan", "/a", {})
        cdn.purge("/a").result()
        
        metrics_str = str(cdn.metrics)
        self.assertIn("Purges=1", metrics_str)
        
        cdn.shutdown()


if __name__ == "__main__":
    unittest.main()
