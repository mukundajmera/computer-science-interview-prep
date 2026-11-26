import unittest
import threading
import sys
import os
import importlib.util
import time

def load_module(version_dir, module_name="distributed_counter"):
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    module_path = os.path.join(base_path, version_dir, f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(f"{version_dir}.{module_name}", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

class TestDistributedCounterAllVersions(unittest.TestCase):
    def setUp(self):
        self.versions = ["v1-basic", "v2-extended", "v3-optimized"]
        
    def test_initial_value(self):
        for version in self.versions:
            module = load_module(version)
            counter = module.DistributedCounter()
            val = counter.get()
            self.assertEqual(val, 0)

    def test_single_thread_increment(self):
        for version in self.versions:
            module = load_module(version)
            counter = module.DistributedCounter()
            for _ in range(100):
                counter.increment()
            self.assertEqual(counter.get(), 100)

    def test_multi_thread_increment(self):
        for version in self.versions:
            module = load_module(version)
            counter = module.DistributedCounter()
            
            def worker():
                for _ in range(1000):
                    counter.increment()
                    
            threads = [threading.Thread(target=worker) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
                
            self.assertEqual(counter.get(), 10000)

    def test_increment_by_value(self):
        for version in self.versions:
            module = load_module(version)
            counter = module.DistributedCounter()
            
            def worker():
                for _ in range(100):
                    counter.increment(5)
                    
            threads = [threading.Thread(target=worker) for _ in range(10)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
                
            self.assertEqual(counter.get(), 5000)

    def test_high_concurrency(self):
        for version in self.versions:
            module = load_module(version)
            counter = module.DistributedCounter()
            
            def worker():
                for i in range(200):
                    counter.increment(1)
                    
            threads = [threading.Thread(target=worker) for _ in range(50)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
                
            self.assertEqual(counter.get(), 10000)
            
    def test_v3_resizing(self):
        module = load_module("v3-optimized")
        counter = module.DistributedCounter()
        
        # Force contention
        counter.NCPU = 16
        
        # Intentionally hold lock to force cell creation
        def blocker():
            if counter.base_lock.acquire():
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
            
        self.assertEqual(counter.get(), 2000)
        # verify cells was created
        self.assertIsNotNone(counter.cells)

if __name__ == '__main__':
    unittest.main()
