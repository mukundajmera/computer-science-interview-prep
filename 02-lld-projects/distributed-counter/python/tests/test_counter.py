import pytest
import threading
import sys
import os
import importlib.util
import time

def load_module(version_dir, module_name="counter"):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    module_path = os.path.join(base_path, version_dir, f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(f"{version_dir}.{module_name}", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

versions = ["v1-basic", "v2-extended", "v3-optimized"]

@pytest.mark.parametrize("version", versions)
def test_initial_value(version):
    module = load_module(version)
    counter = module.Counter()
    val = counter.get()
    assert val == 0

@pytest.mark.parametrize("version", versions)
def test_single_thread_increment(version):
    module = load_module(version)
    counter = module.Counter()
    for _ in range(100):
        counter.increment()
    assert counter.get() == 100

@pytest.mark.parametrize("version", versions)
def test_multi_thread_increment(version):
    module = load_module(version)
    counter = module.Counter()
    
    def worker():
        for _ in range(1000):
            counter.increment()
            
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert counter.get() == 10000

@pytest.mark.parametrize("version", versions)
def test_increment_by_value(version):
    module = load_module(version)
    counter = module.Counter()
    
    def worker():
        for _ in range(100):
            counter.increment(5)
            
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert counter.get() == 5000

@pytest.mark.parametrize("version", versions)
def test_high_concurrency(version):
    module = load_module(version)
    counter = module.Counter()
    
    def worker():
        for i in range(200):
            counter.increment(1)
            
    threads = [threading.Thread(target=worker) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert counter.get() == 10000
    
def test_v3_resizing():
    module = load_module("v3-optimized")
    counter = module.Counter()
    
    # Force contention
    counter.NCPU = 16
    
    # Intentionally hold lock to force cell creation
    def blocker():
        counter.base_lock.acquire()
        time.sleep(0.1)
        counter.base_lock.release()

    def worker():
        for i in range(100):
            counter.increment(1)
            
    threads = [threading.Thread(target=blocker) for _ in range(5)]
    threads.extend([threading.Thread(target=worker) for _ in range(20)])
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert counter.get() == 2000
    # verify cells was created
    assert counter.cells is not None

