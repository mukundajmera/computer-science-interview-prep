import pytest
import threading
from v2_extended.models import Location, Driver, Restaurant, NearestDriverStrategy, DriverManager, FoodDeliveryPlatform, Order, OrderState

def test_nearest_driver():
    rest = Restaurant("R1", Location(0, 0))
    d1 = Driver("D1", Location(0, 10))
    d2 = Driver("D2", Location(0, 5))
    
    strategy = NearestDriverStrategy()
    nearest = strategy.dispatch(rest, [d1, d2])
    
    assert nearest is not None
    assert nearest.id == "D2"

def test_driver_manager():
    strategy = NearestDriverStrategy()
    manager = DriverManager(strategy)
    
    d1 = Driver("D1", Location(0, 5))
    manager.add_driver(d1)
    
    rest = Restaurant("R1", Location(0, 0))
    assigned = manager.assign_driver(rest)
    
    assert assigned is not None
    assert assigned.id == "D1"
    assert not assigned.available

@pytest.fixture
def platform_setup():
    strategy = NearestDriverStrategy()
    manager = DriverManager(strategy)
    shared_driver = Driver("D1", Location(0, 5))
    manager.add_driver(shared_driver)
    platform = FoodDeliveryPlatform(manager)
    rest = Restaurant("R1", Location(0, 0))
    return platform, manager, rest, shared_driver

def test_concurrent_driver_assignment(platform_setup):
    platform, manager, rest, shared_driver = platform_setup
    
    num_threads = 10
    barrier = threading.Barrier(num_threads)
    success_count = 0
    success_lock = threading.Lock()
    
    def process(order_id):
        nonlocal success_count
        order = Order(order_id, 10.0)
        barrier.wait()
        if platform.process_order(order, rest, True, True):
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

def test_duplicate_order_requests(platform_setup):
    platform, manager, rest, shared_driver = platform_setup
    order = Order("O1", 10.0)
    
    first = platform.process_order(order, rest, True, True)
    second = platform.process_order(order, rest, True, True)
    
    assert first is True
    assert second is False
    assert order.final_total == 10.0

def test_late_acceptance_preserves_total(platform_setup):
    platform, manager, rest, shared_driver = platform_setup
    order = Order("O1", 10.0)
    
    success = platform.process_order(order, rest, False, True)
    
    assert success is False
    assert order.final_total == 10.0

def test_unavailable_stock_preserves_total(platform_setup):
    platform, manager, rest, shared_driver = platform_setup
    order = Order("O1", 10.0)
    
    success = platform.process_order(order, rest, True, False)
    
    assert success is False
    assert order.final_total == 10.0
