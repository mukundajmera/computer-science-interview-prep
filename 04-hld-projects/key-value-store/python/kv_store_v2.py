import unittest
import hashlib
import bisect

class HashRing:
    def __init__(self, replicas=3):
        self.replicas = replicas
        self.ring = []
        self.nodes = set()
        
    def add_node(self, node):
        self.nodes.add(node)
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            bisect.insort(self.ring, (key, node))
            
    def remove_node(self, node):
        self.nodes.remove(node)
        self.ring = [(k, n) for k, n in self.ring if n != node]
        
    def get_node(self, key):
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect(self.ring, (h, ""))
        if idx == len(self.ring):
            idx = 0
        return self.ring[idx][1]
        
    def _hash(self, key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

class TestKVStoreV2(unittest.TestCase):
    def test_add_node(self):
        ring = HashRing()
        ring.add_node("node1")
        self.assertEqual(len(ring.nodes), 1)
        
    def test_get_node(self):
        ring = HashRing()
        ring.add_node("node1")
        self.assertEqual(ring.get_node("key1"), "node1")
        
    def test_multiple_nodes(self):
        ring = HashRing()
        ring.add_node("node1")
        ring.add_node("node2")
        ring.add_node("node3")
        nodes = set([ring.get_node(f"k{i}") for i in range(100)])
        self.assertTrue(len(nodes) > 1)
        
    def test_remove_node(self):
        ring = HashRing()
        ring.add_node("node1")
        ring.add_node("node2")
        ring.remove_node("node1")
        self.assertEqual(ring.get_node("key1"), "node2")
        
    def test_vnodes(self):
        ring = HashRing(replicas=5)
        ring.add_node("n1")
        self.assertEqual(len(ring.ring), 5)
        
    def test_empty_ring(self):
        ring = HashRing()
        self.assertIsNone(ring.get_node("k1"))

if __name__ == '__main__':
    unittest.main()
