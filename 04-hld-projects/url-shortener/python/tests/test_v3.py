import unittest
import sys
import os
import threading
import time

# Add repo root to path to allow importing _testutil
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, root_dir)
from _testutil import load_module

v1_mod = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), "../v1-basic/url_shortening_service.py")), "url_shortening_service")
v3_mod = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), "../v3-distributed/distributed_url_service.py")), "distributed_url_service")

class MockDistributedCache(v3_mod.DistributedCache):
    def __init__(self):
        self.store = {}
        
    def get(self, short_code):
        return self.store.get(short_code)
        
    def get_local(self, short_code):
        return self.store.get(short_code)
        
    def put(self, short_code, long_url, ttl_seconds):
        self.store[short_code] = long_url
        
    def evict(self, short_code):
        self.store.pop(short_code, None)
        
    def invalidate_global(self, short_code):
        self.store.pop(short_code, None)
        
    def get_stats(self):
        return v3_mod.CacheStats(hits=0, misses=0, evictions=0)

class MockRegionalService(v3_mod.RegionalService):
    def __init__(self, region_name):
        self.region = region_name
        self.urls = {}
        
    def create_url(self, request, base_url):
        short_code = "dist-123"
        self.urls[short_code] = request.long_url
        return {
            'short_code': short_code,
            'short_url': f"{base_url}/{short_code}",
            'long_url': request.long_url
        }
        
    def get_url(self, short_code):
        if short_code == "error":
            raise Exception("DB error")
        return self.urls.get(short_code)
        
    def get_stats(self, short_code):
        return None
        
    def delete_url(self, short_code):
        return self.urls.pop(short_code, None) is not None
        
    def replicate(self, short_code, long_url):
        self.urls[short_code] = long_url
        
    def get_region(self):
        return self.region

class TestDistributedUrlService(unittest.TestCase):
    def setUp(self):
        self.reg_us_east = MockRegionalService("us-east-1")
        self.reg_us_west = MockRegionalService("us-west-1")
        self.reg_eu_west = MockRegionalService("eu-west-1")
        
        regional_services = {
            "us-east-1": self.reg_us_east,
            "us-west-1": self.reg_us_west,
            "eu-west-1": self.reg_eu_west
        }
        
        self.cache = MockDistributedCache()
        self.service = v3_mod.MultiRegionUrlService(
            current_region="us-east-1",
            regional_services=regional_services,
            cache=self.cache,
            base_url="http://short.url"
        )
    
    def tearDown(self):
        self.service._replication_manager.shutdown()
        
    def test_create_and_replicate(self):
        req = v1_mod.CreateUrlRequest(long_url="https://example.com/dist")
        resp = self.service.create_short_url(req)
        short_code = resp['short_code']
        
        # Verify it's in the local region
        self.assertEqual(self.reg_us_east.urls[short_code], "https://example.com/dist")
        self.assertEqual(self.cache.get(short_code), "https://example.com/dist")
        
        # Wait a bit for async replication
        time.sleep(0.1)
        
        # Verify replicated to other regions
        self.assertEqual(self.reg_us_west.urls[short_code], "https://example.com/dist")
        self.assertEqual(self.reg_eu_west.urls[short_code], "https://example.com/dist")
        
    def test_get_url_from_cache(self):
        self.cache.put("mycode", "https://example.com/cache", 86400)
        
        url = self.service.get_original_url("mycode")
        self.assertEqual(url, "https://example.com/cache")
        
    def test_get_url_miss_cache(self):
        # determine where 'euro' falls to put it in the right region
        data_region = self.service.get_data_region("euro")
        self.service._regional_services[data_region].urls["euro"] = "https://example.com/eu"
        
        url = self.service.get_original_url("euro")
        self.assertEqual(url, "https://example.com/eu")
        # should now be cached
        self.assertEqual(self.cache.get("euro"), "https://example.com/eu")
        
    def test_delete_global(self):
        req = v1_mod.CreateUrlRequest(long_url="https://example.com/del")
        resp = self.service.create_short_url(req)
        short_code = resp['short_code']
        time.sleep(0.1)
        
        deleted = self.service.delete_url(short_code)
        self.assertTrue(deleted)
        
        self.assertIsNone(self.cache.get(short_code))
        self.assertNotIn(short_code, self.reg_us_east.urls)
        self.assertNotIn(short_code, self.reg_us_west.urls)
        
    def test_circuit_breaker_open(self):
        cb = v3_mod.SimpleCircuitBreaker(failure_threshold=2, reset_time_ms=500)
        
        def fail():
            raise ValueError("fail")
            
        def fallback():
            return "fallback"
            
        self.assertEqual(cb.execute(fail, fallback), "fallback")
        self.assertEqual(cb.execute(fail, fallback), "fallback")
        
        self.assertTrue(cb.is_open())
        self.assertEqual(cb.execute(fail, fallback), "fallback") # Returns fallback without running operation
        
    def test_circuit_breaker_reset(self):
        cb = v3_mod.SimpleCircuitBreaker(failure_threshold=1, reset_time_ms=10)
        
        def fail():
            raise ValueError("fail")
            
        def fallback():
            return "fallback"
            
        cb.execute(fail, fallback)
        self.assertTrue(cb.is_open())
        
        # Wait for reset
        time.sleep(0.05)
        self.assertFalse(cb.is_open())
        
        def success():
            return "success"
            
        self.assertEqual(cb.execute(success, fallback), "success")

if __name__ == '__main__':
    unittest.main()
