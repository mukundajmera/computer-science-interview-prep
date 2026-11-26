import unittest
import copy

class VectorClock:
    def __init__(self, clock=None):
        self.clock = clock or {}
        
    def increment(self, node):
        self.clock[node] = self.clock.get(node, 0) + 1
        
    def merge(self, other):
        for k, v in other.clock.items():
            self.clock[k] = max(self.clock.get(k, 0), v)
            
    def compares(self, other):
        # returns True if self <= other, False otherwise
        for k, v in self.clock.items():
            if other.clock.get(k, 0) < v:
                return False
        return True

class Node:
    def __init__(self, name):
        self.name = name
        self.store = {}
        self.hinted = []
        self.is_down = False
        
    def put(self, key, value, vc):
        if self.is_down:
            raise Exception("Node down")
        if key not in self.store or self.store[key][1].compares(vc):
            self.store[key] = (value, vc)
            return True
        return False
        
    def get(self, key):
        if self.is_down:
            raise Exception("Node down")
        return self.store.get(key, None)

class QuorumSystem:
    def __init__(self, nodes, n=3, w=2, r=2):
        self.nodes = {n: Node(n) for n in nodes}
        self.n = n
        self.w = w
        self.r = r
        
    def put(self, key, value, coordinator):
        vc = VectorClock()
        if key in self.nodes[coordinator].store:
            vc = copy.deepcopy(self.nodes[coordinator].store[key][1])
        vc.increment(coordinator)
        
        success = 0
        nodes_tried = list(self.nodes.values())
        for node in nodes_tried:
            try:
                if node.put(key, value, copy.deepcopy(vc)):
                    success += 1
                if success == self.w:
                    break
            except Exception:
                pass
                
        if success < self.w:
            # Hinted handoff logic (simplified)
            for node in nodes_tried:
                if node.is_down:
                    self.nodes[coordinator].hinted.append((node.name, key, value, vc))
        return success >= self.w

    def get(self, key):
        results = []
        for node in self.nodes.values():
            try:
                res = node.get(key)
                if res:
                    results.append(res)
            except Exception:
                pass
        
        if len(results) < self.r:
            return None # Failed to reach quorum
            
        # Conflict resolution logic: return item with highest vector clock
        best_val, best_vc = None, VectorClock()
        for val, vc in results:
            if best_vc.compares(vc):
                best_val, best_vc = val, vc
        return best_val, best_vc

class TestKVStoreV3(unittest.TestCase):
    def test_vector_clock_increment(self):
        vc = VectorClock()
        vc.increment("n1")
        self.assertEqual(vc.clock["n1"], 1)
        
    def test_vector_clock_merge(self):
        vc1 = VectorClock({"n1": 1})
        vc2 = VectorClock({"n2": 2})
        vc1.merge(vc2)
        self.assertEqual(vc1.clock, {"n1": 1, "n2": 2})
        
    def test_quorum_put_get(self):
        qs = QuorumSystem(["n1", "n2", "n3"])
        self.assertTrue(qs.put("k1", "v1", "n1"))
        res = qs.get("k1")
        self.assertIsNotNone(res)
        self.assertEqual(res[0], "v1")
        
    def test_quorum_node_down(self):
        qs = QuorumSystem(["n1", "n2", "n3"], w=2, r=2)
        qs.nodes["n3"].is_down = True
        self.assertTrue(qs.put("k1", "v1", "n1")) # Should still succeed (w=2)
        res = qs.get("k1")
        self.assertIsNotNone(res)
        self.assertEqual(res[0], "v1")
        
    def test_conflict_resolution(self):
        qs = QuorumSystem(["n1", "n2", "n3"])
        vc1 = VectorClock({"n1": 1})
        vc2 = VectorClock({"n1": 1, "n2": 1})
        qs.nodes["n1"].store["k1"] = ("v1", vc1)
        qs.nodes["n2"].store["k1"] = ("v2", vc2)
        # qs.get should resolve to v2 since vc1 <= vc2
        res = qs.get("k1")
        self.assertIsNotNone(res)
        self.assertEqual(res[0], "v2")
        
    def test_hinted_handoff(self):
        qs = QuorumSystem(["n1", "n2", "n3", "n4"], n=3, w=3)
        qs.nodes["n3"].is_down = True
        qs.nodes["n4"].is_down = True
        qs.put("k1", "v1", "n1")
        self.assertTrue(len(qs.nodes["n1"].hinted) > 0)

if __name__ == '__main__':
    unittest.main()
