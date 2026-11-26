import unittest
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from v2.eviction_store import EvictionStore
from v3.sharded_client import Node, ShardedClient

class TestEvictionStore(unittest.TestCase):
    def test_allkeys_lru(self):
        store = EvictionStore(capacity=2, policy="allkeys-lru")
        store.set("a", 1)
        store.set("b", 2)
        store.get("a") # a is now most recently used
        store.set("c", 3) # should evict b
        
        self.assertEqual(store.get("a"), 1)
        self.assertIsNone(store.get("b"))
        self.assertEqual(store.get("c"), 3)
        
    def test_volatile_lru(self):
        store = EvictionStore(capacity=2, policy="volatile-lru")
        store.set("a", 1) # no ttl
        store.set("b", 2, ttl=10) # ttl
        store.set("c", 3) # should evict b
        
        self.assertEqual(store.get("a"), 1)
        self.assertIsNone(store.get("b"))
        self.assertEqual(store.get("c"), 3)
        
    def test_volatile_lru_oom(self):
        store = EvictionStore(capacity=2, policy="volatile-lru")
        store.set("a", 1)
        store.set("b", 2)
        with self.assertRaises(MemoryError):
            store.set("c", 3)
            
    def test_ttl_expiration(self):
        store = EvictionStore(capacity=2)
        store.set("a", 1, ttl=0.1)
        time.sleep(0.15)
        self.assertIsNone(store.get("a"))
        
    def test_capacity_with_expired(self):
        store = EvictionStore(capacity=2)
        store.set("a", 1, ttl=0.1)
        store.set("b", 2)
        time.sleep(0.15)
        store.set("c", 3) # should passively evict a, leaving space
        self.assertEqual(store.get("b"), 2)
        self.assertEqual(store.get("c"), 3)

class TestShardedClient(unittest.TestCase):
    def setUp(self):
        nodes = [Node("node1", "localhost", 6379), Node("node2", "localhost", 6380)]
        self.client = ShardedClient(nodes)
        
    def test_basic_set_get(self):
        res, err = self.client.execute_command("SET", "key1", "val1")
        self.assertEqual(res, "OK")
        res, err = self.client.execute_command("GET", "key1")
        self.assertEqual(res, "val1")
        
    def test_hash_tags(self):
        slot1 = self.client._get_hash_slot("{user:123}:profile")
        slot2 = self.client._get_hash_slot("{user:123}:settings")
        self.assertEqual(slot1, slot2)
        
    def test_hot_key_cache(self):
        self.client.execute_command("SET", "hot", "val")
        # trigger hot key
        for _ in range(6):
            self.client.execute_command("GET", "hot")
            
        self.assertIn("hot", self.client.local_cache)
        self.assertEqual(self.client.local_cache["hot"], "val")
        
    def test_update_hot_key(self):
        self.client.execute_command("SET", "hot2", "val1")
        for _ in range(6):
            self.client.execute_command("GET", "hot2")
            
        self.client.execute_command("SET", "hot2", "val2")
        self.assertEqual(self.client.local_cache["hot2"], "val2")
        
    def test_unknown_command(self):
        res, err = self.client.execute_command("DEL", "key1")
        self.assertEqual(err, "UNKNOWN_COMMAND")
        
    def test_redirect_moved(self):
        # Find a key that goes to node1
        key = "testkey1"
        slot = self.client._get_hash_slot(key)
        correct_node_id = self.client.slots[slot]
        wrong_node_id = "node2" if correct_node_id == "node1" else "node1"
        
        res, err = self.client.execute_command("SET", key, "val", initial_node_id=wrong_node_id)
        self.assertIsNone(res)
        self.assertTrue(err.startswith(f"MOVED {slot}"))
        
        # Now try with correct node
        res, err = self.client.execute_command("SET", key, "val", initial_node_id=correct_node_id)
        self.assertEqual(res, "OK")


if __name__ == '__main__':
    unittest.main()
