import os
import shutil
import pytest
import importlib.util
import sys
import time

def load_module(version):
    module_name = f"lsm_store_{version.replace('-', '_')}"
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", version, "lsm_store.py"))
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

VERSIONS = ["v1-basic", "v2-extended", "v3-optimized"]
TEST_DATA_DIR = "test_lsm_data_py_tmp"

@pytest.fixture(params=VERSIONS)
def store_class(request):
    module = load_module(request.param)
    return module.LSMStore

@pytest.fixture
def test_dir():
    if os.path.isdir(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)
    os.makedirs(TEST_DATA_DIR)
    yield TEST_DATA_DIR
    if os.path.isdir(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)

def test_basic_put_get(store_class, test_dir):
    store = store_class(test_dir, 2)
    store.put("key1", "val1")
    assert store.get("key1") == "val1"

def test_update_key(store_class, test_dir):
    store = store_class(test_dir, 2)
    store.put("key1", "val1")
    store.put("key1", "val2")
    assert store.get("key1") == "val2"

def test_flush(store_class, test_dir):
    store = store_class(test_dir, 2)
    store.put("key1", "val1")
    store.put("key2", "val2") # Flush
    store.put("key3", "val3")
    
    assert store.get("key1") == "val1"
    assert store.get("key2") == "val2"
    assert store.get("key3") == "val3"

def test_delete(store_class, test_dir):
    store = store_class(test_dir, 2)
    store.put("key1", "val1")
    store.delete("key1")
    assert store.get("key1") is None

def test_compaction(store_class, test_dir):
    if "v1" in store_class.__module__:
        return
    store = store_class(test_dir, 2)
    store.put("key1", "val1")
    store.put("key2", "val2") # Flush 1
    time.sleep(0.01)
    
    store.put("key1", "val1_new")
    store.put("key3", "val3") # Flush 2
    time.sleep(0.01)
    
    store.delete("key2")
    store.put("key4", "val4") # Flush 3 -> Compaction (v3)

    assert store.get("key1") == "val1_new"
    assert store.get("key2") is None
    assert store.get("key3") == "val3"
    assert store.get("key4") == "val4"

def test_flush_crash(store_class, test_dir):
    store = store_class(test_dir, 2)
    store.put("key1", "val1")
    
    def crash():
        raise RuntimeError("Flush failed")
        
    if hasattr(store, 'flush_crash_point'):
        store.flush_crash_point = crash
    
        with pytest.raises(RuntimeError) as exc:
            store.put("key2", "val2")
    
        assert "Flush failed" in str(exc.value)
    
        recovered_store = store_class(test_dir, 2)
        assert recovered_store.get("key1") == "val1"
        assert recovered_store.get("key2") == "val2"

def test_corrupt_truncated_records(store_class, test_dir):
    store = store_class(test_dir, 4)
    store.put("key1", "val1")
    store.put("key2", "val2")
    wal = os.path.join(test_dir, "wal.log")
    if os.path.exists(wal):
        with open(wal, "a") as f:
            f.write("corrupt_record_without_equals_sign\n")
            f.write("key3=val3\n")
    
    recovered_store = store_class(test_dir, 4)
    assert recovered_store.get("key1") == "val1"
    assert recovered_store.get("key2") == "val2"
    assert recovered_store.get("key3") == "val3"

def test_duplicate_replay_and_range_boundaries(store_class, test_dir):
    store = store_class(test_dir, 2)
    store.put("key1", "val1")
    store.put("key1", "val2") # duplicate
    store.put("key2", "val2") # flush threshold
    
    recovered_store = store_class(test_dir, 2)
    assert recovered_store.get("key1") == "val2"

def test_tombstones_survive_compaction(store_class, test_dir):
    if "v1" in store_class.__module__:
        return
    store = store_class(test_dir, 2)
    store.put("key1", "val1")
    store.put("key2", "val2") # Flush
    time.sleep(0.01)
    store.delete("key1")
    store.put("key3", "val3") # Flush
    time.sleep(0.01)
    store.put("key4", "val4")
    store.put("key5", "val5") # Flush, trigger compaction
    
    reopened_store = store_class(test_dir, 2)
    assert reopened_store.get("key1") is None

def test_bloom_filter_exact_lookup(store_class, test_dir):
    store = store_class(test_dir, 2)
    store.put("key1", "val1")
    store.put("key2", "val2") # Flush
    assert store.get("key1") == "val1"
    assert store.get("nonexistent") is None
