"""
V3: Dynamic Service Registry with TTL

Production-like registry with TTL-based deregistration.
"""

import time
import uuid
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class EventType(Enum):
    REGISTERED = "REGISTERED"
    DEREGISTERED = "DEREGISTERED"
    EXPIRED = "EXPIRED"


@dataclass
class ServiceInstance:
    """A service instance with TTL."""
    id: str
    service_name: str
    host: str
    port: int
    metadata: Dict[str, str]
    ttl_seconds: float
    expiration_time: float = field(default=0.0)
    
    def __post_init__(self):
        self.expiration_time = time.time() + self.ttl_seconds
    
    def renew(self) -> None:
        self.expiration_time = time.time() + self.ttl_seconds
    
    def is_healthy(self) -> bool:
        return time.time() < self.expiration_time
    
    def __str__(self) -> str:
        return f"{self.host}:{self.port}"


RegistryListener = Callable[[EventType, ServiceInstance], None]


class DynamicServiceRegistry:
    """
    Dynamic service registry with TTL-based deregistration.
    
    Example:
        registry = DynamicServiceRegistry(default_ttl_seconds=5)
        registry.start()
        instance_id = registry.register("api-service", "10.0.0.1", 8080)
        registry.renew("api-service", instance_id)
    """
    
    def __init__(self, default_ttl_seconds: float = 30.0):
        self._registry: Dict[str, Dict[str, ServiceInstance]] = {}
        self._default_ttl = default_ttl_seconds
        self._listeners: List[RegistryListener] = []
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def add_listener(self, listener: RegistryListener) -> None:
        self._listeners.append(listener)

    def register(
        self,
        service_name: str,
        host: str,
        port: int,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Register a service instance, returns instance ID."""
        instance_id = str(uuid.uuid4())[:8]
        instance = ServiceInstance(
            id=instance_id,
            service_name=service_name,
            host=host,
            port=port,
            metadata=metadata or {},
            ttl_seconds=self._default_ttl
        )
        
        with self._lock:
            if service_name not in self._registry:
                self._registry[service_name] = {}
            self._registry[service_name][instance_id] = instance
        
        self._notify_listeners(EventType.REGISTERED, instance)
        print(f"Registered: {service_name}/{instance_id} at {host}:{port}")
        return instance_id

    def renew(self, service_name: str, instance_id: str) -> None:
        """Renew TTL for an instance."""
        with self._lock:
            if service_name in self._registry:
                instance = self._registry[service_name].get(instance_id)
                if instance:
                    instance.renew()

    def deregister(self, service_name: str, instance_id: str) -> None:
        """Deregister a service instance."""
        with self._lock:
            if service_name in self._registry:
                instance = self._registry[service_name].pop(instance_id, None)
                if instance:
                    self._notify_listeners(EventType.DEREGISTERED, instance)
                    print(f"Deregistered: {service_name}/{instance_id}")

    def discover(self, service_name: str) -> List[ServiceInstance]:
        """Discover healthy instances."""
        with self._lock:
            instances = self._registry.get(service_name, {})
            return [i for i in instances.values() if i.is_healthy()]

    def discover_one(self, service_name: str, session_id: str) -> Optional[ServiceInstance]:
        """Discover one instance with sticky session support."""
        instances = self.discover(service_name)
        if not instances:
            return None
        index = abs(hash(session_id)) % len(instances)
        return instances[index]

    def _cleanup_loop(self) -> None:
        while self._running:
            self._cleanup()
            time.sleep(1)

    def _cleanup(self) -> None:
        now = time.time()
        with self._lock:
            for service_name in list(self._registry.keys()):
                for instance_id in list(self._registry[service_name].keys()):
                    instance = self._registry[service_name][instance_id]
                    if now > instance.expiration_time:
                        del self._registry[service_name][instance_id]
                        self._notify_listeners(EventType.EXPIRED, instance)
                        print(f"Expired: {service_name}/{instance_id}")

    def _notify_listeners(self, event_type: EventType, instance: ServiceInstance) -> None:
        for listener in self._listeners:
            listener(event_type, instance)

    def print_registry(self) -> None:
        """Print registry contents."""
        print("\n=== Dynamic Service Registry ===")
        with self._lock:
            for name, instances in self._registry.items():
                print(f"{name}:")
                for instance in instances.values():
                    ttl_remaining = max(0, int(instance.expiration_time - time.time()))
                    meta = f" {instance.metadata}" if instance.metadata else ""
                    print(f"  {instance.id} ({instance.host}:{instance.port}) TTL: {ttl_remaining}s{meta}")


if __name__ == "__main__":
    registry = DynamicServiceRegistry(default_ttl_seconds=5)
    registry.add_listener(lambda t, i: print(f"[EVENT] {t.value}: {i.service_name}/{i.id}"))
    registry.start()
    
    # Register services
    id1 = registry.register("api-service", "10.0.0.1", 8080, {"version": "1.0", "region": "us-east"})
    id2 = registry.register("api-service", "10.0.0.2", 8080, {"version": "1.0", "region": "us-west"})
    
    registry.print_registry()
    
    # Renew only id1
    for _ in range(3):
        time.sleep(2)
        registry.renew("api-service", id1)
        print(f"\nRenewed {id1}")
        registry.print_registry()
    
    # Wait for id2 to expire
    time.sleep(3)
    
    print("\nFinal state:")
    registry.print_registry()
    
    registry.stop()
