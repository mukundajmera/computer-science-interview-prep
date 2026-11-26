"""
V1: Simple Round Robin Load Balancer

A basic load balancer that distributes requests evenly
across available servers in a circular order.

Features:
- Round robin algorithm
- Thread-safe counter
- Simple server pool management

Limitations:
- No health checks
- No server weights
- No consideration of server load
"""

from typing import List
import threading


class RoundRobinLoadBalancer:
    """
    Simple round-robin load balancer.
    
    Example:
        lb = RoundRobinLoadBalancer(["server-a:8080", "server-b:8080"])
        server = lb.get_next_server()
    """
    
    def __init__(self, servers: List[str]):
        """
        Creates a load balancer with the given servers.
        
        Args:
            servers: List of server addresses
        """
        if not servers:
            raise ValueError("Server list cannot be empty")
        
        self._servers: List[str] = list(servers)
        self._current_index: int = 0
        self._lock = threading.Lock()
    
    def get_next_server(self) -> str:
        """
        Gets the next server in round-robin order.
        Thread-safe.
        """
        with self._lock:
            server = self._servers[self._current_index]
            self._current_index = (self._current_index + 1) % len(self._servers)
            return server
    
    def add_server(self, server: str) -> None:
        """Adds a new server to the pool."""
        with self._lock:
            if server not in self._servers:
                self._servers.append(server)
    
    def remove_server(self, server: str) -> None:
        """Removes a server from the pool."""
        with self._lock:
            if server in self._servers:
                self._servers.remove(server)
                if self._current_index >= len(self._servers):
                    self._current_index = 0
    
    @property
    def server_count(self) -> int:
        """Returns current server count."""
        return len(self._servers)
    
    @property
    def servers(self) -> List[str]:
        """Returns all servers."""
        return list(self._servers)


# ============ Demo ============

def main():
    print("=== Round Robin Load Balancer Demo ===\n")
    
    # Create load balancer with 3 servers
    lb = RoundRobinLoadBalancer(["server-a:8080", "server-b:8080", "server-c:8080"])
    
    # Demo 1: Basic round robin
    print("1. Basic Round Robin Distribution:")
    for i in range(1, 10):
        server = lb.get_next_server()
        print(f"   Request {i} → {server}")
    
    # Demo 2: Count distribution
    print("\n2. Distribution over 1000 requests:")
    lb = RoundRobinLoadBalancer(["server-a", "server-b", "server-c"])
    
    distribution = {}
    for _ in range(1000):
        server = lb.get_next_server()
        distribution[server] = distribution.get(server, 0) + 1
    
    for server, count in sorted(distribution.items()):
        print(f"   {server}: {count} requests ({count / 10:.1f}%)")
    
    # Demo 3: Adding/removing servers
    print("\n3. Dynamic Server Pool:")
    print(f"   Initial servers: {lb.servers}")
    
    lb.add_server("server-d")
    print(f"   After adding server-d: {lb.servers}")
    
    lb.remove_server("server-b")
    print(f"   After removing server-b: {lb.servers}")
    
    print("\n   Next 4 requests:")
    for i in range(1, 5):
        print(f"   Request {i} → {lb.get_next_server()}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
