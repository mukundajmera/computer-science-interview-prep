import unittest
import sys
import os
from datetime import datetime, timedelta

# Add repo root to path to allow importing _testutil
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, root_dir)
from _testutil import load_module

v1_mod = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), "../v1-basic/url_shortening_service.py")), "url_shortening_service")

class TestBasicUrlShorteningService(unittest.TestCase):
    def setUp(self):
        self.repo = v1_mod.InMemoryUrlRepository()
        self.generator = v1_mod.CounterBasedGenerator()
        self.service = v1_mod.BasicUrlShorteningService(
            repository=self.repo,
            code_generator=self.generator,
            base_url="http://short.url"
        )
    
    def test_create_short_url_happy_path(self):
        req = v1_mod.CreateUrlRequest(long_url="https://example.com")
        resp = self.service.create_short_url(req)
        
        self.assertIsNotNone(resp.short_code)
        self.assertEqual(resp.long_url, "https://example.com")
        self.assertEqual(resp.short_url, f"http://short.url/{resp.short_code}")
        
        # Verify it's saved
        saved = self.repo.find_by_short_code(resp.short_code)
        self.assertIsNotNone(saved)
        self.assertEqual(saved.long_url, "https://example.com")
        
    def test_create_short_url_custom_alias(self):
        req = v1_mod.CreateUrlRequest(long_url="https://example.com/custom", custom_alias="my-alias")
        resp = self.service.create_short_url(req)
        
        self.assertEqual(resp.short_code, "my-alias")
        self.assertEqual(resp.short_url, "http://short.url/my-alias")
        
    def test_create_short_url_custom_alias_collision(self):
        req1 = v1_mod.CreateUrlRequest(long_url="https://example.com/custom1", custom_alias="my-alias")
        self.service.create_short_url(req1)
        
        req2 = v1_mod.CreateUrlRequest(long_url="https://example.com/custom2", custom_alias="my-alias")
        with self.assertRaises(v1_mod.AliasAlreadyExistsError):
            self.service.create_short_url(req2)
            
    def test_get_original_url(self):
        req = v1_mod.CreateUrlRequest(long_url="https://example.com")
        resp = self.service.create_short_url(req)
        
        original = self.service.get_original_url(resp.short_code)
        self.assertEqual(original, "https://example.com")
        
        # Check click count incremented
        stats = self.service.get_stats(resp.short_code)
        self.assertEqual(stats.click_count, 1)
        
    def test_get_original_url_not_found(self):
        original = self.service.get_original_url("nonexistent")
        self.assertIsNone(original)
        
    def test_url_expiry(self):
        past_time = datetime.utcnow() - timedelta(minutes=5)
        req = v1_mod.CreateUrlRequest(long_url="https://example.com", expires_at=past_time)
        resp = self.service.create_short_url(req)
        
        with self.assertRaises(v1_mod.UrlExpiredError):
            self.service.get_original_url(resp.short_code)

    def test_invalid_url_format(self):
        req = v1_mod.CreateUrlRequest(long_url="not-a-url")
        with self.assertRaises(ValueError):
            self.service.create_short_url(req)

    def test_delete_url(self):
        req = v1_mod.CreateUrlRequest(long_url="https://example.com/delete")
        resp = self.service.create_short_url(req)
        
        self.assertTrue(self.service.delete_url(resp.short_code))
        self.assertFalse(self.service.delete_url(resp.short_code))
        self.assertIsNone(self.service.get_original_url(resp.short_code))

if __name__ == '__main__':
    unittest.main()
