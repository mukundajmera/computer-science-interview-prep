import time
import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from dns_resolver import DnsResolver


class TestDnsResolver(unittest.TestCase):
    def test_cache_hit_before_ttl_expiry(self):
        resolver = DnsResolver({"a.com": ["1.1.1.1", "1.1.1.2"]})
        first = resolver.resolve("a.com", ttl_seconds=1)
        second = resolver.resolve("a.com", ttl_seconds=1)
        self.assertEqual(first, second)

    def test_round_robin_after_ttl_expiry(self):
        resolver = DnsResolver({"a.com": ["1.1.1.1", "1.1.1.2"]})
        first = resolver.resolve("a.com", ttl_seconds=1)
        time.sleep(1.1)
        second = resolver.resolve("a.com", ttl_seconds=1)
        self.assertNotEqual(first, second)

    def test_unknown_domain_returns_none(self):
        resolver = DnsResolver({"a.com": ["1.1.1.1"]})
        self.assertIsNone(resolver.resolve("missing.com"))


if __name__ == '__main__':
    unittest.main()
