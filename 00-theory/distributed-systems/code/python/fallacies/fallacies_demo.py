import time
import json
import zlib
from typing import Any, Dict, List

class NetworkError(Exception):
    """Exception raised for network-related errors."""
    pass

class SecurityError(Exception):
    """Exception raised for security-related errors."""
    pass

class FallaciesSimulator:
    """
    Simulates the 8 Fallacies of Distributed Computing.
    """
    
    def __init__(self, 
                 reliable: bool = False, 
                 latency_ms: int = 50, 
                 bandwidth_limit: int = 1024,
                 simulate_failures: bool = True):
        self.reliable = reliable
        self.latency_ms = latency_ms
        self.bandwidth_limit = bandwidth_limit
        self.simulate_failures = simulate_failures
        self.topology = ["NodeA", "NodeB", "NodeC"]
        self.administrators = {"NodeA": "Alice", "NodeB": "Bob", "NodeC": "Charlie"}
        self.secure = False
        
    def send_message_reliable(self, message: str) -> bool:
        """
        Fallacy 1: The network is reliable.
        Demonstrates that network calls can fail.
        """
        if not self.reliable and self.simulate_failures:
            raise NetworkError("Connection timed out. The network is NOT reliable.")
        return True

    def send_message_latency(self, message: str) -> float:
        """
        Fallacy 2: Latency is zero.
        Demonstrates that sending a message takes time.
        """
        start_time = time.time()
        # Simulate network latency
        if self.latency_ms > 0:
            time.sleep(self.latency_ms / 1000.0)
        end_time = time.time()
        
        return end_time - start_time

    def send_message_bandwidth(self, data: bytes) -> bool:
        """
        Fallacy 3: Bandwidth is infinite.
        Demonstrates that large payloads can exceed capacity.
        """
        if len(data) > self.bandwidth_limit:
            raise NetworkError(f"Payload size {len(data)} bytes exceeds bandwidth limit {self.bandwidth_limit} bytes. Bandwidth is NOT infinite.")
        return True

    def send_message_secure(self, message: str, encrypted: bool = False) -> str:
        """
        Fallacy 4: The network is secure.
        Demonstrates that unencrypted messages can be intercepted/read.
        """
        if not encrypted and not self.secure and self.simulate_failures:
            return f"INTERCEPTED: {message}"
        return message

    def get_topology(self) -> List[str]:
        """
        Fallacy 5: Topology doesn't change.
        Demonstrates that nodes can go down or IP addresses change.
        """
        current_topology = list(self.topology)
        if self.simulate_failures and current_topology:
            # Simulate a node going down (e.g., node crash, network partition)
            current_topology.pop(0)
            
        return current_topology

    def apply_policy(self, node: str, policy: str, admin: str) -> bool:
        """
        Fallacy 6: There is one administrator.
        Demonstrates that coordinating across domains with different admins is hard.
        """
        expected_admin = self.administrators.get(node)
        if not expected_admin:
            raise ValueError(f"Unknown node {node}")
            
        if expected_admin != admin:
            raise SecurityError(f"Unauthorized. {node} is administered by {expected_admin}, not {admin}. There is NOT one administrator.")
        return True

    def send_message_transport_cost(self, message: str) -> int:
        """
        Fallacy 7: Transport cost is zero.
        Demonstrates that serialization and connection setup consume resources (CPU/Memory).
        Returns simulated cost metric.
        """
        # Cost includes serialization and connection overhead
        serialized = json.dumps({"payload": message}).encode('utf-8')
        compressed = zlib.compress(serialized)
        
        cost = len(compressed) * 10  # Arbitrary cost metric to represent CPU/memory/time
        return cost

    def parse_message_homogeneous(self, payload: bytes, sender_format: str) -> Dict[str, Any]:
        """
        Fallacy 8: The network is homogeneous.
        Demonstrates that different nodes might use different formats 
        (e.g. JSON vs XML, or binary serialization formats).
        """
        if sender_format != "JSON":
            raise ValueError(f"Cannot parse format {sender_format}. Expected JSON. The network is NOT homogeneous.")
            
        try:
            return json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError:
            raise ValueError("Failed to parse JSON. Heterogeneous network issue.")
