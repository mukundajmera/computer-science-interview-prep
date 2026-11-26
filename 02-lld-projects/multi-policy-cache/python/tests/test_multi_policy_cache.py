import pytest
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../v1-basic')))
for module_name in ["multi_policy_cache"]:
    sys.modules.pop(module_name, None)

from multi_policy_cache import MultiPolicyCache, EvictionPolicy

def test_lru_eviction():
    cache = MultiPolicyCache(capacity=3, policy=EvictionPolicy.LRU)
    cache.put("A", "1")
    cache.put("B", "2")
    cache.put("C", "3")
    cache.get("A")
    cache.put("D", "4")
    
    assert cache.get("B") is None
    assert cache.get("A") == "1"
    assert cache.get("C") == "3"
    assert cache.get("D") == "4"
    cache.shutdown()

def test_fifo_eviction():
    cache = MultiPolicyCache(capacity=3, policy=EvictionPolicy.FIFO)
    cache.put("A", "1")
    cache.put("B", "2")
    cache.put("C", "3")
    cache.get("A")
    cache.put("D", "4")
    
    assert cache.get("A") is None
    assert cache.get("B") == "2"
    cache.shutdown()

def test_lfu_eviction():
    cache = MultiPolicyCache(capacity=3, policy=EvictionPolicy.LFU)
    cache.put("A", "1")
    cache.put("B", "2")
    cache.put("C", "3")
    cache.get("A") # freq 2
    cache.get("A") # freq 3
    cache.get("B") # freq 2
    cache.put("D", "4") # evicts C (freq 1)
    
    assert cache.get("C") is None
    assert cache.get("A") == "1"
    assert cache.get("B") == "2"
    assert cache.get("D") == "4"
    cache.shutdown()

def test_policy_swap():
    cache = MultiPolicyCache(capacity=3, policy=EvictionPolicy.FIFO)
    cache.put("A", "1")
    time.sleep(0.01)
    cache.put("B", "2")
    time.sleep(0.01)
    cache.put("C", "3")
    
    cache.get("A") # A accessed
    
    cache.change_policy(EvictionPolicy.LRU)
    cache.put("D", "4") # evicts B (least recently accessed)
    
    assert cache.get("B") is None
    assert cache.get("A") == "1"
    assert cache.get("C") == "3"
    assert cache.get("D") == "4"
    cache.shutdown()

def test_ttl_expiration_passive():
    cache = MultiPolicyCache(capacity=3, policy=EvictionPolicy.LRU)
    cache.put("A", "1", ttl_ms=100)
    cache.put("B", "2")
    
    time.sleep(0.2)
    
    assert cache.get("A") is None
    assert cache.get("B") == "2"
    cache.shutdown()

def test_ttl_expiration_active():
    cache = MultiPolicyCache(capacity=3, policy=EvictionPolicy.LRU)
    cache.put("A", "1", ttl_ms=100)
    
    assert cache.size() == 1
    time.sleep(1.5) # Wait for background thread
    
    assert cache.size() == 0
    cache.shutdown()
