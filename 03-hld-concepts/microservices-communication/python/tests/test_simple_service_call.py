import pytest
import sys
import os

# Dynamic sys.path to resolve 'v1_simple'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from simple_service_call import SimpleServiceCall


def test_successful_service_call():
    """Test successful registration and call of a single service."""
    client = SimpleServiceCall()
    client.register_service("auth", lambda req: f"Token for {req}")
    
    response = client.call("auth", "user123")
    assert response == "Token for user123"


def test_service_not_found_raises_error():
    """Test calling an unregistered service raises RuntimeError."""
    client = SimpleServiceCall()
    with pytest.raises(RuntimeError, match="Service not found: unknown-service"):
        client.call("unknown-service", "request data")


def test_multiple_services():
    """Test registering and calling multiple services."""
    client = SimpleServiceCall()
    client.register_service("users", lambda req: "Alice")
    client.register_service("orders", lambda req: "Order456")
    
    user_resp = client.call("users", "id=1")
    order_resp = client.call("orders", "id=456")
    
    assert user_resp == "Alice"
    assert order_resp == "Order456"
