import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from simple_registry import SimpleServiceRegistry

def test_register_and_discover():
    registry = SimpleServiceRegistry()
    registry.register("auth-service", "192.168.1.10", 9000)
    registry.register("auth-service", "192.168.1.11", 9000)
    registry.register("payment-service", "192.168.1.12", 9001)
    
    auth_instances = registry.discover("auth-service")
    assert len(auth_instances) == 2
    assert any(i.host == "192.168.1.10" and i.port == 9000 for i in auth_instances)
    assert any(i.host == "192.168.1.11" and i.port == 9000 for i in auth_instances)
    
    payment_instances = registry.discover("payment-service")
    assert len(payment_instances) == 1
    assert payment_instances[0].host == "192.168.1.12"
    assert payment_instances[0].port == 9001
    
    # Discovering unknown service returns empty list
    assert len(registry.discover("unknown-service")) == 0

def test_deregister():
    registry = SimpleServiceRegistry()
    registry.register("auth-service", "192.168.1.10", 9000)
    registry.register("auth-service", "192.168.1.11", 9000)
    
    # Deregister one instance
    registry.deregister("auth-service", "192.168.1.10", 9000)
    auth_instances = registry.discover("auth-service")
    assert len(auth_instances) == 1
    assert auth_instances[0].host == "192.168.1.11"
    assert auth_instances[0].port == 9000
    
    # Deregister a non-existent instance does nothing
    registry.deregister("auth-service", "192.168.1.10", 9000)
    assert len(registry.discover("auth-service")) == 1
    
    # Deregister a non-existent service does nothing
    registry.deregister("unknown-service", "192.168.1.10", 9000)
    assert len(registry.discover("auth-service")) == 1

def test_discover_one():
    registry = SimpleServiceRegistry()
    registry.register("auth-service", "192.168.1.10", 9000)
    
    instance = registry.discover_one("auth-service")
    assert instance.host == "192.168.1.10"
    assert instance.port == 9000
    
    # Discover one with multiple instances will return one of them based on hash
    registry.register("auth-service", "192.168.1.11", 9000)
    instance2 = registry.discover_one("auth-service")
    assert instance2.host in ["192.168.1.10", "192.168.1.11"]
    
    with pytest.raises(RuntimeError):
        registry.discover_one("unknown-service")
