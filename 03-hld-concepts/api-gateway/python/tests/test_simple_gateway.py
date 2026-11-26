import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from simple_gateway import SimpleGateway

def test_unauthenticated_request_rejected():
    gateway = SimpleGateway()
    gateway.add_route("/users", "http://user-service:8080", auth_required=True, max_requests=10)

    response = gateway.handle("/users/1", is_authenticated=False)

    assert response == "401 Unauthorized"

def test_authenticated_request_allowed_and_rate_limited():
    gateway = SimpleGateway()
    gateway.add_route("/users", "http://user-service:8080", auth_required=True, max_requests=2)

    # First request
    response1 = gateway.handle("/users/1", is_authenticated=True)
    assert response1 == "200 Forward -> http://user-service:8080"

    # Second request
    response2 = gateway.handle("/users/2", is_authenticated=True)
    assert response2 == "200 Forward -> http://user-service:8080"

    # Third request - should be rate limited
    response3 = gateway.handle("/users/3", is_authenticated=True)
    assert response3 == "429 Too Many Requests"

def test_unknown_route_returns_not_found():
    gateway = SimpleGateway()
    gateway.add_route("/users", "http://user-service:8080", auth_required=False, max_requests=10)

    response = gateway.handle("/products/1", is_authenticated=False)

    assert response == "404 Not Found"
