import os
import sys
import time
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from simple_redis_cache import SimpleRedisCache

@pytest.fixture
def cache():
    return SimpleRedisCache()

def test_set_and_get(cache):
    cache.set("key1", "value1", 1.0)
    assert cache.get("key1") == "value1"
    
    assert cache.get("missing") is None

def test_ttl_expiration(cache):
    cache.set("key2", "value2", 0.1) # 100ms TTL
    assert cache.get("key2") == "value2"
    
    time.sleep(0.15) # Wait for expiration
    
    assert cache.get("key2") is None

def test_set_if_absent(cache):
    assert cache.set_if_absent("key3", "value3", 1.0) is True
    assert cache.get("key3") == "value3"
    
    assert cache.set_if_absent("key3", "newValue", 1.0) is False
    assert cache.get("key3") == "value3"

def test_increment(cache):
    assert cache.increment("counter1", 1, 1.0) == 1
    assert cache.increment("counter1", 4, 1.0) == 5
    assert cache.get("counter1") == "5"
    assert cache.increment("counter1", -2, 1.0) == 3
    assert cache.get("counter1") == "3"

def test_invalid_ttl(cache):
    with pytest.raises(ValueError):
        cache.set("key4", "value4", 0)
        
    with pytest.raises(ValueError):
        cache.set("key4", "value4", -1.0)
