"""
V1: Simple Service Registry

Basic in-memory service registry.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ServiceInstance:
    """A service instance."""
    host: str
    port: int
    
    def __str__(self) -> str:
        return f"{self.host}:{self.port}"


class SimpleServiceRegistry:
    """
    Simple in-memory service registry.
    
    Example:
        registry = SimpleServiceRegistry()
        registry.register("user-service", "10.0.0.1", 8080)
        instances = registry.discover("user-service")
    """
    
    def __init__(self):
        self._registry: Dict[str, List[ServiceInstance]] = {}

    def register(self, service_name: str, host: str, port: int) -> None:
        """Register a service instance."""
        if service_name not in self._registry:
            self._registry[service_name] = []
        self._registry[service_name].append(ServiceInstance(host, port))
        print(f"Registered: {service_name} at {host}:{port}")

    def deregister(self, service_name: str, host: str, port: int) -> None:
        """Deregister a service instance."""
        if service_name in self._registry:
            self._registry[service_name] = [
                i for i in self._registry[service_name]
                if not (i.host == host and i.port == port)
            ]
            print(f"Deregistered: {service_name} at {host}:{port}")

    def discover(self, service_name: str) -> List[ServiceInstance]:
        """Discover all instances of a service."""
        return list(self._registry.get(service_name, []))

    def discover_one(self, service_name: str) -> ServiceInstance:
        """Discover one instance (round-robin)."""
        instances = self.discover(service_name)
        if not instances:
            raise RuntimeError(f"No instances found for: {service_name}")
        return instances[abs(hash(service_name)) % len(instances)]

    def print_registry(self) -> None:
        """Print registry contents."""
        print("\n=== Service Registry ===")
        for name, instances in self._registry.items():
            print(f"{name}: {[str(i) for i in instances]}")


if __name__ == "__main__":
    registry = SimpleServiceRegistry()
    
    registry.register("user-service", "10.0.0.1", 8080)
    registry.register("user-service", "10.0.0.2", 8080)
    registry.register("order-service", "10.0.0.3", 8081)
    
    registry.print_registry()
    
    print("\nDiscovering user-service:")
    print(registry.discover("user-service"))
    
    print("\nDiscovering one instance:")
    print(registry.discover_one("user-service"))
