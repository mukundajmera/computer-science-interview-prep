"""
V2: Weighted Round Robin Load Balancer with Health Checks

A more realistic load balancer that:
- Supports weighted distribution
- Performs health checks
- Removes unhealthy servers automatically

Features:
- Weighted round robin algorithm
- Configurable server weights
- Background health checking
- Thread-safe operations
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
import threading
import time
from concurrent.futures import ThreadPoolExecutor


@dataclass
class Server:
    """Server representation with weight and health status."""
    address: str
    weight: int
    healthy: bool = True
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_check_time: float = 0
    
    def mark_healthy(self) -> None:
        self.healthy = True
        self.consecutive_failures = 0
    
    def mark_unhealthy(self) -> None:
        self.healthy = False
    
    def record_failure(self) -> None:
        self.consecutive_failures += 1
        self.consecutive_successes = 0
    
    def record_success(self) -> None:
        self.consecutive_successes += 1
        self.consecutive_failures = 0


@dataclass
class HealthCheckConfig:
    """Health check configuration."""
    interval_seconds: float = 5.0
    timeout_seconds: float = 2.0
    unhealthy_threshold: int = 3
    healthy_threshold: int = 2
    checker: Callable[[str], bool] = field(default=lambda addr: True)


class WeightedLoadBalancer:
    """
    Weighted round robin load balancer with health checks.
    
    Example:
        servers = [
            Server("high-capacity", 5),
            Server("medium-capacity", 3),
            Server("low-capacity", 2)
        ]
        config = HealthCheckConfig(interval_seconds=5)
        lb = WeightedLoadBalancer(servers, config)
        
        server = lb.get_next_server()
    """
    
    def __init__(self, servers: List[Server], config: HealthCheckConfig):
        self._servers = list(servers)
        self._healthy_servers: List[Server] = []
        self._current_index = 0
        self._lock = threading.Lock()
        self._config = config
        self._running = True
        self._stop_event = threading.Event()
        
        # Request tracking
        self._request_counts: Dict[str, int] = {s.address: 0 for s in servers}
        
        # Build initial healthy list
        self._rebuild_healthy_list()
        
        # Start health checker
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="health-check")
        self._executor.submit(self._health_check_loop)
    
    def get_next_server(self) -> Optional[str]:
        """
        Gets the next server using weighted round robin.
        Only returns healthy servers.
        """
        with self._lock:
            if not self._healthy_servers:
                return None
            
            server = self._healthy_servers[self._current_index]
            self._current_index = (self._current_index + 1) % len(self._healthy_servers)
            self._request_counts[server.address] += 1
            
            return server.address
    
    def _rebuild_healthy_list(self) -> None:
        """Rebuilds the weighted healthy server list."""
        self._healthy_servers = []
        for server in self._servers:
            if server.healthy:
                # Add server multiple times based on weight
                for _ in range(server.weight):
                    self._healthy_servers.append(server)
        self._current_index = 0
    
    def _health_check_loop(self) -> None:
        """Background health check loop."""
        while self._running:
            if self._stop_event.wait(self._config.interval_seconds):
                break
            if not self._running:
                break
            self._perform_health_checks()
    
    def _perform_health_checks(self) -> None:
        """Performs health checks on all servers."""
        changed = False
        
        for server in self._servers:
            try:
                is_healthy = self._config.checker(server.address)
            except Exception:
                is_healthy = False
            
            server.last_check_time = time.time()
            
            if is_healthy:
                server.record_success()
                if not server.healthy:
                    if server.consecutive_successes >= self._config.healthy_threshold:
                        server.mark_healthy()
                        changed = True
                        print(f"Server became healthy: {server.address}")
            else:
                server.record_failure()
                if server.healthy:
                    if server.consecutive_failures >= self._config.unhealthy_threshold:
                        server.mark_unhealthy()
                        changed = True
                        print(f"Server became unhealthy: {server.address}")
        
        if changed:
            with self._lock:
                self._rebuild_healthy_list()
    
    def mark_server_unhealthy(self, address: str) -> None:
        """Manually marks a server as unhealthy."""
        with self._lock:
            for server in self._servers:
                if server.address == address:
                    server.mark_unhealthy()
                    self._rebuild_healthy_list()
                    break
    
    def get_request_distribution(self) -> Dict[str, int]:
        """Returns request distribution statistics."""
        return dict(self._request_counts)
    
    def get_all_servers(self) -> List[Server]:
        """Returns all servers."""
        return list(self._servers)
    
    def get_healthy_server_count(self) -> int:
        """Returns count of healthy servers."""
        return sum(1 for s in self._servers if s.healthy)
    
    def shutdown(self) -> None:
        """Shuts down the health checker."""
        self._running = False
        self._stop_event.set()
        self._executor.shutdown(wait=True)


# ============ Demo ============

def main():
    print("=== Weighted Load Balancer Demo ===\n")
    
    # Demo 1: Weighted distribution
    print("1. Weighted Distribution:")
    demo_weighted_distribution()
    
    # Demo 2: Health checks
    print("\n2. Health Checks:")
    demo_health_checks()
    
    print("\n=== Demo Complete ===")


def demo_weighted_distribution():
    servers = [
        Server("high-capacity-server", 5),   # 50% traffic
        Server("medium-capacity-server", 3), # 30% traffic
        Server("low-capacity-server", 2)     # 20% traffic
    ]
    
    config = HealthCheckConfig(interval_seconds=1000)  # Disable for demo
    lb = WeightedLoadBalancer(servers, config)
    
    # Send 1000 requests
    distribution = {}
    for _ in range(1000):
        server = lb.get_next_server()
        distribution[server] = distribution.get(server, 0) + 1
    
    print("   Server weights: high=5, medium=3, low=2 (total=10)")
    print("   Distribution over 1000 requests:")
    for server, count in sorted(distribution.items()):
        print(f"   {server}: {count} ({count / 10:.1f}%)")
    
    lb.shutdown()


def demo_health_checks():
    # Track which servers are "healthy" in our simulation
    simulated_healthy = {"server-1", "server-2", "server-3"}
    
    servers = [
        Server("server-1", 1),
        Server("server-2", 1),
        Server("server-3", 1)
    ]
    
    config = HealthCheckConfig(
        interval_seconds=1,
        unhealthy_threshold=2,
        checker=lambda addr: addr in simulated_healthy
    )
    
    lb = WeightedLoadBalancer(servers, config)
    
    print("   Initial: All 3 servers healthy")
    print(f"   Healthy count: {lb.get_healthy_server_count()}")
    
    # Simulate server-2 failing
    print("\n   Simulating server-2 failure...")
    simulated_healthy.remove("server-2")
    
    time.sleep(3)
    
    print(f"   Healthy count after failure: {lb.get_healthy_server_count()}")
    
    # Show which servers are getting traffic
    print("\n   Requests (server-2 should not receive any):")
    for _ in range(6):
        print(f"   → {lb.get_next_server()}")
    
    lb.shutdown()


if __name__ == "__main__":
    main()
