import pytest
import threading
import importlib.util
import os

spec = importlib.util.spec_from_file_location("models", os.path.join(os.path.dirname(__file__), "..", "v1-basic", "models.py"))
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)

spec2 = importlib.util.spec_from_file_location("food_delivery_platform", os.path.join(os.path.dirname(__file__), "..", "v1-basic", "food_delivery_platform.py"))
fdp = importlib.util.module_from_spec(spec2)
fdp.models = models
spec2.loader.exec_module(fdp)


def test_concurrent_driver_assignment():
    platform = fdp.FoodDeliveryPlatform()
    shared_driver_id = "D1"
    
    num_threads = 10
    barrier = threading.Barrier(num_threads)
    success_count = 0
    success_lock = threading.Lock()
    
    def process(order_id):
        nonlocal success_count
        order = models.Order(order_id, 10.0)
        barrier.wait()
        if platform.process_order(order, shared_driver_id, True, True):
            with success_lock:
                success_count += 1
                
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=process, args=(f"O{i}",))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join(timeout=5)
        
    assert success_count == 1

def test_duplicate_order_requests():
    platform = fdp.FoodDeliveryPlatform()
    driver_id = "D1"
    order = models.Order("O1", 10.0)
    
    first = platform.process_order(order, driver_id, True, True)
    second = platform.process_order(order, driver_id, True, True)
    
    assert first is True
    assert second is False
    assert order.final_total == 10.0

def test_late_acceptance_preserves_total():
    platform = fdp.FoodDeliveryPlatform()
    driver_id = "D1"
    order = models.Order("O1", 10.0)
    
    success = platform.process_order(order, driver_id, False, True)
    
    assert success is False
    assert order.final_total == 10.0

def test_unavailable_stock_preserves_total():
    platform = fdp.FoodDeliveryPlatform()
    driver_id = "D1"
    order = models.Order("O1", 10.0)
    
    success = platform.process_order(order, driver_id, True, False)
    
    assert success is False
    assert order.final_total == 10.0
