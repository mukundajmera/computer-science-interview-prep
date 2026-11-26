"""
V2: Service Registry with Health Checks

Registry with heartbeat-based health monitoring.
"""

import time
import threading
from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class ServiceInstance:
    """A service instance with health status."""
    id: str
    host: str
    port: int
    healthy: bool = True
    last_heartbeat: float = field(default_factory=time.time)


class HealthCheckRegistry:
    """
    Registry with heartbeat-based health monitoring.
    
    Example:
        registry = HealthCheckRegistry(health_check_interval=1, timeout=3)
        registry.start()
        registry.register("user-service", "user-1", "10.0.0.1", 8080)
        registry.heartbeat("user-service", "user-1")
    """
    
    def __init__(self, health_check_interval: float = 1.0, timeout: float = 3.0):
        self._registry: Dict[str, Dict[str, ServiceInstance]] = {}
        self._health_check_interval = health_check_interval
        self._timeout = timeout
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start health check loop."""
        self._running = True
        self._thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop health check loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def register(self, service_name: str, instance_id: str, host: str, port: int) -> None:
        """Register a service instance."""
        with self._lock:
            if service_name not in self._registry:
                self._registry[service_name] = {}
            self._registry[service_name][instance_id] = ServiceInstance(instance_id, host, port)
        print(f"Registered: {service_name}/{instance_id}")

    def heartbeat(self, service_name: str, instance_id: str) -> None:
        """Update heartbeat for an instance."""
        with self._lock:
            instances = self._registry.get(service_name)
            if instances:
                instance = instances.get(instance_id)
                if instance:
                    instance.last_heartbeat = time.time()
                    instance.healthy = True

    def deregister(self, service_name: str, instance_id: str) -> None:
        """Deregister a service instance."""
        with self._lock:
            if service_name in self._registry:
                self._registry[service_name].pop(instance_id, None)
                print(f"Deregistered: {service_name}/{instance_id}")

    def discover_healthy(self, service_name: str) -> List[ServiceInstance]:
        """Discover healthy instances."""
        with self._lock:
            instances = self._registry.get(service_name, {})
            return [i for i in instances.values() if i.healthy]

    def _health_check_loop(self) -> None:
        while self._running:
            self._check_health()
            time.sleep(self._health_check_interval)

    def _check_health(self) -> None:
        now = time.time()
        with self._lock:
            for service_name, instances in self._registry.items():
                for instance in instances.values():
                    if now - instance.last_heartbeat > self._timeout:
                        if instance.healthy:
                            instance.healthy = False
                            print(f"UNHEALTHY: {service_name}/{instance.id}")

    def print_registry(self) -> None:
        """Print registry with health status."""
        print("\n=== Registry with Health ===")
        with self._lock:
            for name, instances in self._registry.items():
                print(f"{name}:")
                for instance in instances.values():
                    status = "HEALTHY" if instance.healthy else "UNHEALTHY"
                    print(f"  {instance.id} ({instance.host}:{instance.port}) - {status}")


if __name__ == "__main__":
    registry = HealthCheckRegistry(health_check_interval=1, timeout=3)
    registry.start()
    
    registry.register("user-service", "user-1", "10.0.0.1", 8080)
    registry.register("user-service", "user-2", "10.0.0.2", 8080)
    
    # Simulate heartbeats for user-1 only
    for _ in range(5):
        time.sleep(1)
        registry.heartbeat("user-service", "user-1")
    
    registry.print_registry()
    
    print("\nHealthy instances:")
    print(registry.discover_healthy("user-service"))
    
    registry.stop()
