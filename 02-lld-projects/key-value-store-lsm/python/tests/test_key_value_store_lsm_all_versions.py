import os
import shutil
import pytest
import importlib.util
import sys

def load_module():
    module_name = f"key_value_store_lsm"
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "v2-extended", "key_value_store_lsm.py"))
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

@pytest.fixture
def store_class():
    module = load_module()
    return module.KeyValueStoreLsm

@pytest.fixture
def test_dir():
    d = "test_lsm_data_py_2"
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    yield d
    if os.path.exists(d):
        shutil.rmtree(d)

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
