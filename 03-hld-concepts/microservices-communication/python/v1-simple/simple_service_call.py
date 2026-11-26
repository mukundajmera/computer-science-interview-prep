"""
V1: Simple Service Call

Basic HTTP-like service-to-service call simulation.
"""

from typing import Dict, Callable


class SimpleServiceCall:
    """Simple service-to-service communication."""
    
    def __init__(self):
        self._services: Dict[str, Callable[[str], str]] = {}
    
    def register_service(self, name: str, handler: Callable[[str], str]) -> None:
        """Register a service handler."""
        self._services[name] = handler
    
    def call(self, service_name: str, request: str) -> str:
        """Call a service."""
        handler = self._services.get(service_name)
        if handler is None:
            raise RuntimeError(f"Service not found: {service_name}")
        
        print(f"Calling {service_name} with: {request}")
        response = handler(request)
        print(f"Response from {service_name}: {response}")
        return response


if __name__ == "__main__":
    client = SimpleServiceCall()
    
    client.register_service("user-service", lambda req: "User: Alice")
    client.register_service("order-service", lambda req: "Order: #123")
    
    client.call("user-service", "getUser?id=1")
    client.call("order-service", "getOrder?id=123")
