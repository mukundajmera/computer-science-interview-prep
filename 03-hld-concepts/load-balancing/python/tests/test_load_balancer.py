"""
Unit Tests for Load Balancer Implementations
"""

import unittest
import sys
import os
import subprocess

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-realistic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-production'))


class TestRoundRobinLoadBalancer(unittest.TestCase):
    """Tests for RoundRobinLoadBalancer."""
    
    def test_even_distribution(self):
        """Should distribute evenly across servers."""
        from round_robin_lb import RoundRobinLoadBalancer
        
        lb = RoundRobinLoadBalancer(["A", "B", "C"])
        
        counts = {}
        for _ in range(300):
            server = lb.get_next_server()
            counts[server] = counts.get(server, 0) + 1
        
        self.assertEqual(counts["A"], 100)
        self.assertEqual(counts["B"], 100)
        self.assertEqual(counts["C"], 100)
    
    def test_add_server(self):
        """Should add servers dynamically."""
        from round_robin_lb import RoundRobinLoadBalancer
        
        lb = RoundRobinLoadBalancer(["A", "B"])
        lb.add_server("C")
        
        self.assertEqual(lb.server_count, 3)
        self.assertIn("C", lb.servers)
    
    def test_remove_server(self):
        """Should remove servers dynamically."""
        from round_robin_lb import RoundRobinLoadBalancer
        
        lb = RoundRobinLoadBalancer(["A", "B", "C"])
        lb.remove_server("B")
        
        self.assertEqual(lb.server_count, 2)
        self.assertNotIn("B", lb.servers)
    
    def test_empty_server_list_raises(self):
        """Should raise error for empty server list."""
        from round_robin_lb import RoundRobinLoadBalancer
        
        with self.assertRaises(ValueError):
            RoundRobinLoadBalancer([])


class TestWeightedLoadBalancer(unittest.TestCase):
    """Tests for WeightedLoadBalancer."""

    def test_shutdown_allows_process_exit(self):
        """Shutdown should not leave health-check threads blocking exit."""
        version_dir = os.path.join(os.path.dirname(__file__), '..', 'v2-realistic')
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            [version_dir, env.get("PYTHONPATH", "")]
        )

        subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from weighted_lb import WeightedLoadBalancer, Server, HealthCheckConfig; "
                    "lb = WeightedLoadBalancer([Server('A', 1)], "
                    "HealthCheckConfig(interval_seconds=60)); "
                    "lb.shutdown()"
                ),
            ],
            env=env,
            timeout=2,
            check=True,
        )
    
    def test_weighted_distribution(self):
        """Should distribute according to weights."""
        from weighted_lb import WeightedLoadBalancer, Server, HealthCheckConfig
        
        servers = [
            Server("A", 5),  # 50%
            Server("B", 3),  # 30%
            Server("C", 2),  # 20%
        ]
        
        config = HealthCheckConfig(interval_seconds=1000)
        lb = WeightedLoadBalancer(servers, config)
        
        try:
            counts = {}
            for _ in range(1000):
                server = lb.get_next_server()
                counts[server] = counts.get(server, 0) + 1
            
            # Allow 5% tolerance
            self.assertAlmostEqual(counts["A"], 500, delta=50)
            self.assertAlmostEqual(counts["B"], 300, delta=50)
            self.assertAlmostEqual(counts["C"], 200, delta=50)
        finally:
            lb.shutdown()
    
    def test_skip_unhealthy(self):
        """Should skip unhealthy servers."""
        from weighted_lb import WeightedLoadBalancer, Server, HealthCheckConfig
        
        servers = [
            Server("A", 1),
            Server("B", 1),
            Server("C", 1),
        ]
        
        config = HealthCheckConfig(interval_seconds=1000)
        lb = WeightedLoadBalancer(servers, config)
        
        try:
            lb.mark_server_unhealthy("B")
            
            for _ in range(100):
                server = lb.get_next_server()
                self.assertNotEqual(server, "B")
        finally:
            lb.shutdown()


class TestConsistentHashingLB(unittest.TestCase):
    """Tests for ConsistentHashingLB."""

    def test_shutdown_allows_process_exit(self):
        """Shutdown should not leave health-check threads blocking exit."""
        version_dir = os.path.join(os.path.dirname(__file__), '..', 'v3-production')
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            [version_dir, env.get("PYTHONPATH", "")]
        )

        subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from consistent_hashing_lb import ConsistentHashingLB, HealthCheckConfig; "
                    "lb = ConsistentHashingLB(config=HealthCheckConfig(interval_ms=60000)); "
                    "lb.shutdown()"
                ),
            ],
            env=env,
            timeout=2,
            check=True,
        )
    
    def test_sticky_sessions(self):
        """Same key should always go to same server."""
        from consistent_hashing_lb import ConsistentHashingLB, HealthCheckConfig
        
        config = HealthCheckConfig(interval_ms=60000)
        lb = ConsistentHashingLB(virtual_nodes_per_server=100, config=config)
        
        lb.add_server("A", 1)
        lb.add_server("B", 1)
        lb.add_server("C", 1)
        
        try:
            key = "user-123"
            server1 = lb.get_server_for_key(key)
            server2 = lb.get_server_for_key(key)
            server3 = lb.get_server_for_key(key)
            
            self.assertEqual(server1, server2)
            self.assertEqual(server2, server3)
        finally:
            lb.shutdown()
    
    def test_minimal_redistribution(self):
        """Adding server should minimally redistribute keys."""
        from consistent_hashing_lb import ConsistentHashingLB, HealthCheckConfig
        
        config = HealthCheckConfig(interval_ms=60000)
        lb = ConsistentHashingLB(virtual_nodes_per_server=100, config=config)
        
        lb.add_server("A", 1)
        lb.add_server("B", 1)
        lb.add_server("C", 1)
        
        try:
            # Record original mapping
            original = {}
            for i in range(1000):
                key = f"key-{i}"
                original[key] = lb.get_server_for_key(key)
            
            # Add fourth server
            lb.add_server("D", 1)
            
            changed = 0
            for key, orig_server in original.items():
                if lb.get_server_for_key(key) != orig_server:
                    changed += 1
            
            # Should be approximately 25% (1/4)
            # Allow some tolerance
            self.assertLess(changed, 350)
        finally:
            lb.shutdown()
    
    def test_all_algorithms(self):
        """All algorithms should return valid servers."""
        from consistent_hashing_lb import ConsistentHashingLB, HealthCheckConfig, Algorithm
        
        config = HealthCheckConfig(interval_ms=60000)
        lb = ConsistentHashingLB(virtual_nodes_per_server=100, config=config)
        
        lb.add_server("A", 1)
        lb.add_server("B", 1)
        
        try:
            for algo in Algorithm:
                lb.set_algorithm(algo)
                server = lb.get_server()
                self.assertIn(server, ["A", "B"])
        finally:
            lb.shutdown()


if __name__ == '__main__':
    unittest.main()
