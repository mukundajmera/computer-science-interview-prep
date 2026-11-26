"""
V3: Production Load Balancer with Consistent Hashing

A production-ready load balancer featuring:
- Multiple load balancing algorithms
- Consistent hashing for sticky sessions
- Virtual nodes for even distribution
- Health checking
- Connection tracking
- Comprehensive metrics

This demonstrates patterns used in production systems like
Nginx, HAProxy, and cloud load balancers.
"""

import hashlib
import threading
import time
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import bisect


class Algorithm(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    CONSISTENT_HASH = "consistent_hash"
    RANDOM = "random"


@dataclass
class ServerNode:
    """Server node with metadata."""
    address: str
    weight: int = 1
    healthy: bool = True
    failure_count: int = 0
    success_count: int = 0
    total_requests: int = 0
    last_response_time_ms: float = 0
    
    def mark_healthy(self) -> None:
        self.healthy = True
        self.failure_count = 0
    
    def mark_unhealthy(self) -> None:
        self.healthy = False
    
    def record_success(self, response_time_ms: float) -> None:
        self.success_count += 1
        self.failure_count = 0
        self.last_response_time_ms = response_time_ms
    
    def record_failure(self) -> None:
        self.failure_count += 1


@dataclass
class HealthCheckConfig:
    """Health check configuration."""
    interval_ms: int = 5000
    timeout_ms: int = 2000
    unhealthy_threshold: int = 3
    healthy_threshold: int = 2
    checker: Callable[[str, int], bool] = field(default=lambda addr, timeout: True)


class Metrics:
    """Thread-safe metrics tracking."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._total_requests = 0
        self._failed_requests = 0
        self._server_requests: Dict[str, int] = {}
    
    def record_request(self, server: str, success: bool) -> None:
        with self._lock:
            self._total_requests += 1
            if not success:
                self._failed_requests += 1
            self._server_requests[server] = self._server_requests.get(server, 0) + 1
    
    @property
    def total_requests(self) -> int:
        return self._total_requests
    
    @property
    def failed_requests(self) -> int:
        return self._failed_requests
    
    def success_rate(self) -> float:
        if self._total_requests == 0:
            return 100.0
        return (self._total_requests - self._failed_requests) * 100.0 / self._total_requests
    
    def get_distribution(self) -> Dict[str, int]:
        with self._lock:
            return dict(self._server_requests)


class ConsistentHashingLB:
    """
    Production load balancer with consistent hashing.
    
    Features:
    - Multiple algorithms (round robin, least connections, consistent hash, random)
    - Consistent hashing with virtual nodes for sticky sessions
    - Health checking with automatic failover
    - Connection tracking for least connections algorithm
    - Comprehensive metrics
    
    Example:
        config = HealthCheckConfig(interval_ms=5000)
        lb = ConsistentHashingLB(virtual_nodes_per_server=100, config=config)
        
        lb.add_server("server-a", weight=1)
        lb.add_server("server-b", weight=2)
        
        # Sticky session (same user always goes to same server)
        server = lb.get_server_for_key("user-123")
        
        # Load balanced
        server = lb.get_server()
    """
    
    def __init__(
        self,
        virtual_nodes_per_server: int = 100,
        config: Optional[HealthCheckConfig] = None
    ):
        self._virtual_nodes = virtual_nodes_per_server
        self._config = config or HealthCheckConfig()
        
        # Consistent hash ring (sorted list of (hash, address) tuples)
        self._ring_hashes: List[int] = []
        self._ring_servers: Dict[int, str] = {}
        
        self._servers: Dict[str, ServerNode] = {}
        self._active_connections: Dict[str, int] = {}
        self._lock = threading.RLock()
        
        self._metrics = Metrics()
        self._algorithm = Algorithm.CONSISTENT_HASH
        self._round_robin_index = 0
        
        self._running = True
        self._stop_event = threading.Event()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="lb-health")
        self._executor.submit(self._health_check_loop)
    
    def _hash(self, key: str) -> int:
        """Compute hash using MD5."""
        digest = hashlib.md5(key.encode('utf-8')).digest()
        return int.from_bytes(digest[:4], 'big')
    
    def add_server(self, address: str, weight: int = 1) -> None:
        """Adds a server to the load balancer."""
        with self._lock:
            node = ServerNode(address=address, weight=weight)
            self._servers[address] = node
            self._active_connections[address] = 0
            
            # Add virtual nodes to hash ring
            for i in range(self._virtual_nodes * weight):
                hash_val = self._hash(f"{address}#{i}")
                idx = bisect.bisect_left(self._ring_hashes, hash_val)
                self._ring_hashes.insert(idx, hash_val)
                self._ring_servers[hash_val] = address
    
    def remove_server(self, address: str) -> None:
        """Removes a server from the load balancer."""
        with self._lock:
            if address in self._servers:
                del self._servers[address]
                del self._active_connections[address]
                
                # Remove from hash ring
                hashes_to_remove = [
                    h for h, addr in self._ring_servers.items() 
                    if addr == address
                ]
                for h in hashes_to_remove:
                    del self._ring_servers[h]
                    self._ring_hashes.remove(h)
    
    def get_server_for_key(self, key: str) -> Optional[str]:
        """
        Gets a server for the given key using consistent hashing.
        Same key always maps to same server (unless server removed).
        """
        with self._lock:
            if not self._ring_hashes:
                return None
            
            hash_val = self._hash(key)
            
            # Find first server clockwise from hash
            idx = bisect.bisect_left(self._ring_hashes, hash_val)
            if idx >= len(self._ring_hashes):
                idx = 0
            
            ring_hash = self._ring_hashes[idx]
            server = self._ring_servers[ring_hash]
            
            node = self._servers.get(server)
            if node is None or not node.healthy:
                server = self._get_next_healthy_server(idx)
            
            if server:
                node = self._servers.get(server)
                if node:
                    node.total_requests += 1
            
            return server
    
    def _get_next_healthy_server(self, start_idx: int) -> Optional[str]:
        """Find next healthy server in the ring."""
        if not self._ring_hashes:
            return None
        
        for i in range(len(self._ring_hashes)):
            idx = (start_idx + i) % len(self._ring_hashes)
            ring_hash = self._ring_hashes[idx]
            server = self._ring_servers[ring_hash]
            node = self._servers.get(server)
            if node and node.healthy:
                return server
        
        return None
    
    def get_server(self) -> Optional[str]:
        """Gets a server using the configured algorithm."""
        if self._algorithm == Algorithm.ROUND_ROBIN:
            return self._get_server_round_robin()
        elif self._algorithm == Algorithm.LEAST_CONNECTIONS:
            return self._get_server_least_connections()
        elif self._algorithm == Algorithm.RANDOM:
            return self._get_server_random()
        else:
            # Default: consistent hash with random key
            return self.get_server_for_key(str(random.random()))
    
    def _get_server_round_robin(self) -> Optional[str]:
        healthy = self._get_healthy_servers()
        if not healthy:
            return None
        
        with self._lock:
            server = healthy[self._round_robin_index % len(healthy)]
            self._round_robin_index = (self._round_robin_index + 1) % len(healthy)
            return server
    
    def _get_server_least_connections(self) -> Optional[str]:
        healthy = self._get_healthy_servers()
        if not healthy:
            return None
        
        min_conns = float('inf')
        selected = None
        for addr in healthy:
            conns = self._active_connections.get(addr, 0)
            if conns < min_conns:
                min_conns = conns
                selected = addr
        
        return selected
    
    def _get_server_random(self) -> Optional[str]:
        healthy = self._get_healthy_servers()
        if not healthy:
            return None
        return random.choice(healthy)
    
    def _get_healthy_servers(self) -> List[str]:
        return [addr for addr, node in self._servers.items() if node.healthy]
    
    def connection_started(self, server: str) -> None:
        """Marks a connection as started."""
        if server in self._active_connections:
            self._active_connections[server] += 1
    
    def connection_ended(self, server: str) -> None:
        """Marks a connection as ended."""
        if server in self._active_connections:
            self._active_connections[server] = max(0, self._active_connections[server] - 1)
    
    def record_success(self, server: str, response_time_ms: float) -> None:
        """Reports a successful request."""
        node = self._servers.get(server)
        if node:
            node.record_success(response_time_ms)
        self._metrics.record_request(server, True)
    
    def record_failure(self, server: str) -> None:
        """Reports a failed request."""
        node = self._servers.get(server)
        if node:
            node.record_failure()
            if node.failure_count >= self._config.unhealthy_threshold:
                node.mark_unhealthy()
        self._metrics.record_request(server, False)
    
    def _health_check_loop(self) -> None:
        """Background health check loop."""
        while self._running:
            if self._stop_event.wait(self._config.interval_ms / 1000.0):
                break
            if not self._running:
                break
            self._perform_health_checks()
    
    def _perform_health_checks(self) -> None:
        """Performs health checks on all servers."""
        for node in self._servers.values():
            try:
                is_healthy = self._config.checker(
                    node.address,
                    self._config.timeout_ms
                )
            except Exception:
                is_healthy = False
            
            if is_healthy:
                if not node.healthy:
                    node.success_count += 1
                    if node.success_count >= self._config.healthy_threshold:
                        node.mark_healthy()
                else:
                    node.failure_count = 0
            else:
                node.record_failure()
                if node.healthy and node.failure_count >= self._config.unhealthy_threshold:
                    node.mark_unhealthy()
    
    def set_algorithm(self, algorithm: Algorithm) -> None:
        self._algorithm = algorithm
    
    @property
    def metrics(self) -> Metrics:
        return self._metrics
    
    @property
    def server_count(self) -> int:
        return len(self._servers)
    
    @property
    def healthy_server_count(self) -> int:
        return len(self._get_healthy_servers())
    
    def shutdown(self) -> None:
        """Shuts down the load balancer."""
        self._running = False
        self._stop_event.set()
        self._executor.shutdown(wait=True)


# ============ Demo ============

def main():
    print("=== Consistent Hashing Load Balancer Demo ===\n")
    
    # Demo 1: Consistent hashing for sticky sessions
    print("1. Consistent Hashing - Sticky Sessions:")
    demo_consistent_hashing()
    
    # Demo 2: Minimal redistribution
    print("\n2. Minimal Redistribution on Server Change:")
    demo_minimal_redistribution()
    
    # Demo 3: Algorithm comparison
    print("\n3. Algorithm Comparison:")
    demo_algorithms()
    
    print("\n=== Demo Complete ===")


def demo_consistent_hashing():
    config = HealthCheckConfig(interval_ms=60000)  # Disable for demo
    lb = ConsistentHashingLB(virtual_nodes_per_server=100, config=config)
    
    lb.add_server("server-a", 1)
    lb.add_server("server-b", 1)
    lb.add_server("server-c", 1)
    
    user_ids = ["user-123", "user-456", "user-789"]
    
    print("   User ID → Server mapping (consistent):")
    for user_id in user_ids:
        server1 = lb.get_server_for_key(user_id)
        server2 = lb.get_server_for_key(user_id)
        server3 = lb.get_server_for_key(user_id)
        consistent = server1 == server2 == server3
        print(f"   {user_id} → {server1} (consistent: {consistent})")
    
    lb.shutdown()


def demo_minimal_redistribution():
    config = HealthCheckConfig(interval_ms=60000)
    lb = ConsistentHashingLB(virtual_nodes_per_server=100, config=config)
    
    lb.add_server("server-a", 1)
    lb.add_server("server-b", 1)
    lb.add_server("server-c", 1)
    
    # Track original mapping
    original_mapping = {}
    for i in range(1000):
        key = f"key-{i}"
        original_mapping[key] = lb.get_server_for_key(key)
    
    print("   Original: 3 servers, 1000 keys distributed")
    count_distribution(original_mapping)
    
    # Add fourth server
    lb.add_server("server-d", 1)
    
    changed = 0
    for key, orig_server in original_mapping.items():
        new_server = lb.get_server_for_key(key)
        if new_server != orig_server:
            changed += 1
    
    print(f"\n   After adding server-d: {changed} keys remapped ({changed / 10:.1f}%)")
    print("   Expected ~25% with consistent hashing (vs 75%+ with modulo)")
    
    lb.shutdown()


def count_distribution(mapping: Dict[str, str]) -> None:
    counts = {}
    for server in mapping.values():
        counts[server] = counts.get(server, 0) + 1
    for server, count in sorted(counts.items()):
        print(f"   {server}: {count} keys")


def demo_algorithms():
    config = HealthCheckConfig(interval_ms=60000)
    lb = ConsistentHashingLB(virtual_nodes_per_server=100, config=config)
    
    lb.add_server("server-a", 1)
    lb.add_server("server-b", 1)
    lb.add_server("server-c", 1)
    
    for algo in Algorithm:
        lb.set_algorithm(algo)
        
        distribution = {}
        for _ in range(300):
            server = lb.get_server()
            distribution[server] = distribution.get(server, 0) + 1
        
        print(f"   {algo.value}:")
        for server, count in sorted(distribution.items()):
            print(f"      {server}: {count}")
    
    lb.shutdown()


if __name__ == "__main__":
    main()
