import pytest
import time
import sys
import os
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))
for module_name in ["multi_policy_cache"]:
    sys.modules.pop(module_name, None)

from multi_policy_cache import MultiPolicyCache, EvictionPolicy

def test_v2_lfu_tie_breaking():
    cache = MultiPolicyCache(capacity=3, policy=EvictionPolicy.LFU)
    cache.put("A", "1")
    cache.put("B", "2")
    cache.put("C", "3")
    
    # All have freq=1. LRU order: A, B, C (C is MRU, A is LRU).
    # Since tie-breaking is LRU, A should be evicted first.
    cache.put("D", "4")
    assert cache.get("A") is None
    assert cache.get("B") == "2"
    assert cache.get("C") == "3"
    assert cache.get("D") == "4"
    cache.shutdown()

def test_v2_lfu_frequency_increments():
    cache = MultiPolicyCache(capacity=3, policy=EvictionPolicy.LFU)
    cache.put("A", "1")
    cache.put("B", "2")
    cache.put("C", "3")
    
    cache.get("A") # freq 2
    cache.get("A") # freq 3
    cache.get("B") # freq 2
    
    # C is freq 1, A is 3, B is 2
    cache.put("D", "4") # Evicts C
    assert cache.get("C") is None
    assert cache.get("A") == "1"
    assert cache.get("B") == "2"
    assert cache.get("D") == "4"
    cache.shutdown()

def test_v2_policy_hot_swapping():
    cache = MultiPolicyCache(capacity=3, policy=EvictionPolicy.FIFO)
    cache.put("A", "1")
    time.sleep(0.01)
    cache.put("B", "2")
    time.sleep(0.01)
    cache.put("C", "3")
    
    cache.get("A") # Access A, doesn't change FIFO order
    
    # Swap to LRU
    cache.change_policy(EvictionPolicy.LRU)
    cache.put("D", "4") # Evicts B, because B is least recently accessed (A was just accessed)
    
    assert cache.get("B") is None
    assert cache.get("A") == "1"
    assert cache.get("C") == "3"
    assert cache.get("D") == "4"
    cache.shutdown()

def test_v2_lfu_policy_hot_swapping():
    cache = MultiPolicyCache(capacity=3, policy=EvictionPolicy.LRU)
    cache.put("A", "1")
    cache.put("B", "2")
    cache.put("C", "3")
    
    cache.get("A")
    cache.get("A")
    cache.get("B")
    
    # Swap to LFU
    cache.change_policy(EvictionPolicy.LFU)
    
    cache.put("D", "4") # Evicts C, as it was least recently accessed (implicit LRU tiebreaker)
    
    assert cache.get("C") is None
    assert cache.get("A") == "1"
    assert cache.get("B") == "2"
    assert cache.get("D") == "4"
    cache.shutdown()
