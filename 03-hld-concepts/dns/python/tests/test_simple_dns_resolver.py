import os
import sys
import time

# Add the target directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from simple_dns_resolver import SimpleDnsResolver

def test_authoritative_miss_returns_none():
    resolver = SimpleDnsResolver()
    assert resolver.resolve("unknown.com", 1.0) is None

def test_authoritative_hit_and_cache_hit():
    resolver = SimpleDnsResolver()
    resolver.upsert_authoritative_record("test.com", "1.2.3.4")

    # First resolve: AUTHORITATIVE_HIT
    result1 = resolver.resolve("test.com", 10.0)
    assert result1 == "1.2.3.4"

    # Update authoritative record to verify cache is being used
    resolver.upsert_authoritative_record("test.com", "5.6.7.8")

    # Second resolve: CACHE_HIT
    result2 = resolver.resolve("test.com", 10.0)
    assert result2 == "1.2.3.4" # Should still return cached value

def test_cache_expiration():
    resolver = SimpleDnsResolver()
    resolver.upsert_authoritative_record("expire.com", "9.9.9.9")

    # Resolve with small TTL
    assert resolver.resolve("expire.com", 0.1) == "9.9.9.9"

    # Wait for TTL to expire
    time.sleep(0.15)

    # Update authoritative to verify we get the new value after cache miss
    resolver.upsert_authoritative_record("expire.com", "8.8.8.8")

    # Resolve again: CACHE_STALE -> AUTHORITATIVE_HIT
    assert resolver.resolve("expire.com", 10.0) == "8.8.8.8"
