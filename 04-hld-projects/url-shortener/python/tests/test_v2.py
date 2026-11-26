import unittest
import sys
import os
import time
from datetime import datetime, timedelta

# Add repo root to path to allow importing _testutil
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, root_dir)
from _testutil import load_module

v1_mod = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), "../v1-basic/url_shortening_service.py")), "url_shortening_service")
v2_mod = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), "../v2-scaled/cached_url_service.py")), "cached_url_service")

class TestCachedUrlShorteningService(unittest.TestCase):
    def setUp(self):
        self.repo = v1_mod.InMemoryUrlRepository()
        self.generator = v1_mod.CounterBasedGenerator()
        self.cache = v2_mod.InMemoryUrlCache()
        self.queue = v2_mod.InMemoryMessageQueue()
        self.service = v2_mod.CachedUrlShorteningService(
            repository=self.repo,
            code_generator=self.generator,
            cache=self.cache,
            message_queue=self.queue,
            base_url="http://short.url"
        )
    
    def test_create_and_cache(self):
        req = v1_mod.CreateUrlRequest(long_url="https://example.com/cached")
        resp = self.service.create_short_url(req)
        
        self.assertIsNotNone(resp['short_code'])
        
        # Verify it's in cache (write-through)
        self.assertTrue(self.cache.exists(resp['short_code']))
        self.assertEqual(self.cache.get(resp['short_code']), "https://example.com/cached")
        
    def test_get_from_cache_hit(self):
        req = v1_mod.CreateUrlRequest(long_url="https://example.com/hit")
        resp = self.service.create_short_url(req)
        short_code = resp['short_code']
        
        # clear queue
        self.queue.drain()
        
        original = self.service.get_original_url(short_code)
        self.assertEqual(original, "https://example.com/hit")
        
        events = self.queue.drain()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].short_code, short_code)
        
    def test_get_from_cache_miss_and_populate(self):
        req = v1_mod.CreateUrlRequest(long_url="https://example.com/miss")
        resp = self.service.create_short_url(req)
        short_code = resp['short_code']
        
        # Evict manually to force a miss
        self.cache.evict(short_code)
        self.assertFalse(self.cache.exists(short_code))
        
        self.queue.drain()
        original = self.service.get_original_url(short_code)
        self.assertEqual(original, "https://example.com/miss")
        
        # Verify it populated the cache
        self.assertTrue(self.cache.exists(short_code))
        
        events = self.queue.drain()
        self.assertEqual(len(events), 1)
        
    def test_evict_on_delete(self):
        req = v1_mod.CreateUrlRequest(long_url="https://example.com/delete")
        resp = self.service.create_short_url(req)
        short_code = resp['short_code']
        
        self.assertTrue(self.cache.exists(short_code))
        self.service.delete_url(short_code)
        
        self.assertFalse(self.cache.exists(short_code))
        
    def test_expired_url_evicts_cache(self):
        past_time = datetime.utcnow() - timedelta(minutes=5)
        req = v1_mod.CreateUrlRequest(long_url="https://example.com/expired", expires_at=past_time)
        resp = self.service.create_short_url(req)
        short_code = resp['short_code']
        
        # Manually clear cache so it hits DB and throws UrlExpiredError
        self.cache.evict(short_code)
        
        with self.assertRaises(v2_mod.UrlExpiredError):
            self.service.get_original_url(short_code)
            
    def test_custom_alias_cached(self):
        req = v1_mod.CreateUrlRequest(long_url="https://example.com/custom", custom_alias="my-cached")
        resp = self.service.create_short_url(req)
        
        self.assertEqual(resp['short_code'], "my-cached")
        self.assertTrue(self.cache.exists("my-cached"))
        
        original = self.service.get_original_url("my-cached")
        self.assertEqual(original, "https://example.com/custom")
        
if __name__ == '__main__':
    unittest.main()
