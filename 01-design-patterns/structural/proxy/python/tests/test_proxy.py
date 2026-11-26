"""Tests for Proxy Pattern implementations."""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-variant'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-advanced'))


class TestV1VirtualProxy(unittest.TestCase):
    """Tests for V1 Basic Virtual Proxy."""

    def test_virtual_proxy_defers_loading(self):
        from proxy_demo import ProxyImage

        proxy = ProxyImage("test.jpg")

        self.assertIsNone(proxy._real)


class TestV2ProtectionProxy(unittest.TestCase):
    """Tests for V2 Variant Protection Proxy."""

    def test_reader_can_read_but_not_write(self):
        from protection_proxy import ProtectedDocumentProxy, RealDocument, User

        document = RealDocument("test.txt")
        reader = User("reader", {"reader"})
        proxy = ProtectedDocumentProxy(document, reader)

        self.assertEqual(proxy.read(), "Document content for: test.txt")
        with self.assertRaises(PermissionError):
            proxy.write("hack")

    def test_admin_can_delete_document(self):
        from protection_proxy import ProtectedDocumentProxy, RealDocument, User

        document = RealDocument("secret.txt")
        admin = User("admin", {"admin"})
        proxy = ProtectedDocumentProxy(document, admin)

        self.assertEqual(proxy.delete(), "Document deleted: secret.txt")


class TestV3CachingProxy(unittest.TestCase):
    """Tests for V3 Advanced Caching Proxy."""

    def test_repeated_fetch_uses_cache(self):
        from caching_proxy import CachingDataServiceProxy, DatabaseService

        cached = CachingDataServiceProxy(DatabaseService())

        self.assertEqual(cached.fetch_data("user:1"), "Alice")
        self.assertEqual(cached.fetch_data("user:1"), "Alice")

        self.assertEqual(cached.hits, 1)
        self.assertEqual(cached.misses, 1)
        self.assertEqual(cached.hit_rate, 50.0)

    def test_update_invalidates_cached_value(self):
        from caching_proxy import CachingDataServiceProxy, DatabaseService

        cached = CachingDataServiceProxy(DatabaseService())
        cached.fetch_data("user:1")
        cached.update_data("user:1", "Alicia")

        self.assertEqual(cached.fetch_data("user:1"), "Alicia")
        self.assertEqual(cached.misses, 2)


if __name__ == "__main__":
    unittest.main()
