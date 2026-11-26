import os
import shutil
import pytest

# Adjust sys.path to find v1_simple correctly since hyphenated paths can be tricky
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from lsm_key_store import LsmKeyStore, BloomFilter

@pytest.fixture
def store():
    test_dir = "test_lsm_data"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    s = LsmKeyStore(memtable_threshold=3, data_dir=test_dir)
    yield s
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

def test_bloom_filter():
    bf = BloomFilter(size=100, hash_count=3)
    bf.add("test_key")
    assert bf.might_contain("test_key") is True
    assert bf.might_contain("missing_key") is False

def test_put_and_get(store):
    store.put("key1", "value1")
    store.put("key2", "value2")

    assert store.get("key1") == "value1"
    assert store.get("key2") == "value2"
    assert store.get("missing") is None

def test_delete(store):
    store.put("key1", "value1")
    store.delete("key1")
    assert store.get("key1") is None

def test_sstable_flush(store):
    # Threshold is 3
    store.put("k1", "v1")
    store.put("k2", "v2")
    store.put("k3", "v3") # This should trigger a flush

    assert len(store.sstables) == 1
    assert len(store.memtable) == 0
    assert not os.path.exists(store.wal_filename)

    # Still accessible
    assert store.get("k1") == "v1"
    assert store.get("k3") == "v3"

def test_scan(store):
    store.put("a", "1")
    store.put("b", "2")
    store.put("c", "3") # flush
    store.put("d", "4")
    store.put("e", "5")

    # Overwrite and delete
    store.put("c", "33")
    store.delete("d")

    results = store.scan("b", "e")
    # Expected: b:2, c:33, e:5
    assert results == [("b", "2"), ("c", "33"), ("e", "5")]

def test_wal_recovery():
    test_dir = "test_lsm_recovery_data"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    s1 = LsmKeyStore(memtable_threshold=5, data_dir=test_dir)
    s1.put("r1", "rv1")
    s1.put("r2", "rv2")

    # Verify WAL was created
    assert os.path.exists(s1.wal_filename)

    # Create new store instance with same dir to simulate recovery
    s2 = LsmKeyStore(memtable_threshold=5, data_dir=test_dir)
    assert s2.get("r1") == "rv1"
    assert s2.get("r2") == "rv2"

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
