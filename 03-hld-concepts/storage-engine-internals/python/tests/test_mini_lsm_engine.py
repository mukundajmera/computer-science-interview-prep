import unittest
import sys
import os

# Adjusting sys.path to be able to import the storage module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.mini_lsm_engine import MiniLsmEngine, BloomFilter, TOMBSTONE

class TestMiniLsmEngine(unittest.TestCase):

    def test_in_memory_retrieval(self):
        engine = MiniLsmEngine(mem_table_threshold=1000)
        engine.put("key1", "value1")
        engine.put("key2", "value2")

        self.assertEqual(engine.get("key1"), "value1")
        self.assertEqual(engine.get("key2"), "value2")
        self.assertIsNone(engine.get("key3"))
        self.assertEqual(engine.get_ss_tables_count(), 0)

    def test_sstable_point_lookup_after_flush(self):
        engine = MiniLsmEngine(mem_table_threshold=10)
        engine.put("key1", "val1") # 8 bytes
        engine.put("key2", "val2") # 8 bytes -> flush key1

        self.assertEqual(engine.get("key1"), "val1")
        self.assertEqual(engine.get("key2"), "val2")
        self.assertGreaterEqual(engine.get_ss_tables_count(), 1)

    def test_tombstone_deletion(self):
        engine = MiniLsmEngine(mem_table_threshold=100)
        engine.put("key1", "value1")
        self.assertEqual(engine.get("key1"), "value1")

        engine.delete("key1")
        self.assertIsNone(engine.get("key1"))

        engine.put("key2", "value2")
        engine.put("key3", "value3")
        engine.put("key4", "value4")
        
        self.assertIsNone(engine.get("key1"))

    def test_compaction_deduplication(self):
        engine = MiniLsmEngine(mem_table_threshold=15)
        engine.put("key1", "v1")
        engine.put("key2", "v2") 
        engine.put("key1", "v1-new") 
        engine.put("key3", "v3") 
        engine.delete("key2")
        engine.put("key4", "v4") 

        self.assertEqual(engine.get("key1"), "v1-new")
        self.assertIsNone(engine.get("key2"))
        self.assertEqual(engine.get("key3"), "v3")
        self.assertGreater(engine.get_ss_tables_count(), 1)

        engine.compact()

        self.assertEqual(engine.get_ss_tables_count(), 1)
        self.assertEqual(engine.get("key1"), "v1-new")
        self.assertIsNone(engine.get("key2"))
        self.assertEqual(engine.get("key3"), "v3")
        self.assertEqual(engine.get("key4"), "v4")

    def test_bloom_filter_skipping(self):
        bf = BloomFilter(size=100, num_hashes=3)
        bf.add("existing_key")
        self.assertTrue(bf.might_contain("existing_key"))
        self.assertFalse(bf.might_contain("non_existing_key"))

if __name__ == '__main__':
    unittest.main()
