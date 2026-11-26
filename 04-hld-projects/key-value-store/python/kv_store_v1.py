import unittest
import time

class WAL:
    def __init__(self):
        self.entries = []
    
    def append(self, key, value):
        self.entries.append((key, value))

class LSMStore:
    def __init__(self):
        self.memtable = {}
        self.wal = WAL()
    
    def put(self, key, value):
        self.wal.append(key, value)
        self.memtable[key] = value
        
    def get(self, key):
        return self.memtable.get(key, None)

class TestKVStoreV1(unittest.TestCase):
    def test_put_get(self):
        store = LSMStore()
        store.put("k1", "v1")
        self.assertEqual(store.get("k1"), "v1")
        
    def test_overwrite(self):
        store = LSMStore()
        store.put("k1", "v1")
        store.put("k1", "v2")
        self.assertEqual(store.get("k1"), "v2")
        
    def test_not_found(self):
        store = LSMStore()
        self.assertIsNone(store.get("k2"))
        
    def test_wal_append(self):
        store = LSMStore()
        store.put("k1", "v1")
        self.assertEqual(len(store.wal.entries), 1)
        self.assertEqual(store.wal.entries[0], ("k1", "v1"))
        
    def test_multiple_puts(self):
        store = LSMStore()
        for i in range(10):
            store.put(f"k{i}", f"v{i}")
        self.assertEqual(store.get("k5"), "v5")
        
    def test_wal_multiple(self):
        store = LSMStore()
        for i in range(5):
            store.put(f"k{i}", f"v{i}")
        self.assertEqual(len(store.wal.entries), 5)

if __name__ == '__main__':
    unittest.main()
