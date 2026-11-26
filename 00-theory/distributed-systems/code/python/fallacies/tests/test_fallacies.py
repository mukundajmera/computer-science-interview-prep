import unittest
import json
import importlib.util
import sys
import os

# Dynamically import fallacies_demo to handle the strict pathing rules
current_dir = os.path.dirname(os.path.abspath(__file__))
demo_path = os.path.join(os.path.dirname(current_dir), 'fallacies_demo.py')

spec = importlib.util.spec_from_file_location("fallacies_demo", demo_path)
fallacies_demo = importlib.util.module_from_spec(spec)
sys.modules["fallacies_demo"] = fallacies_demo
spec.loader.exec_module(fallacies_demo)

from fallacies_demo import FallaciesSimulator, NetworkError, SecurityError

class TestFallaciesSimulator(unittest.TestCase):
    
    def setUp(self):
        self.simulator = FallaciesSimulator()
        self.reliable_simulator = FallaciesSimulator(reliable=True, simulate_failures=False, latency_ms=0)

    def test_fallacy_1_network_is_reliable(self):
        """Test Fallacy 1: The network is reliable."""
        # Unreliable network throws an error
        with self.assertRaises(NetworkError):
            self.simulator.send_message_reliable("Hello")
            
        # Reliable network succeeds
        self.assertTrue(self.reliable_simulator.send_message_reliable("Hello"))

    def test_fallacy_2_latency_is_zero(self):
        """Test Fallacy 2: Latency is zero."""
        # Significant latency exists
        latency = self.simulator.send_message_latency("Hello")
        self.assertGreaterEqual(latency, 0.05) # ~50ms
        
        # Zero latency when simulated as reliable
        zero_latency = self.reliable_simulator.send_message_latency("Hello")
        self.assertLess(zero_latency, 0.01)

    def test_fallacy_3_bandwidth_is_infinite(self):
        """Test Fallacy 3: Bandwidth is infinite."""
        small_payload = b"a" * 500
        large_payload = b"a" * 2000
        
        # Small payload succeeds
        self.assertTrue(self.simulator.send_message_bandwidth(small_payload))
        
        # Large payload exceeds bandwidth limit
        with self.assertRaises(NetworkError):
            self.simulator.send_message_bandwidth(large_payload)

    def test_fallacy_4_network_is_secure(self):
        """Test Fallacy 4: The network is secure."""
        # Unencrypted message is intercepted
        result = self.simulator.send_message_secure("SecretData", encrypted=False)
        self.assertEqual(result, "INTERCEPTED: SecretData")
        
        # Encrypted message goes through
        secure_result = self.simulator.send_message_secure("SecretData", encrypted=True)
        self.assertEqual(secure_result, "SecretData")

    def test_fallacy_5_topology_doesnt_change(self):
        """Test Fallacy 5: Topology doesn't change."""
        initial_topology = ["NodeA", "NodeB", "NodeC"]
        
        # Topology changes under failure conditions (NodeA drops)
        new_topology = self.simulator.get_topology()
        self.assertNotEqual(initial_topology, new_topology)
        self.assertEqual(new_topology, ["NodeB", "NodeC"])
        
        # Topology remains the same when no failures
        stable_topology = self.reliable_simulator.get_topology()
        self.assertEqual(initial_topology, stable_topology)

    def test_fallacy_6_one_administrator(self):
        """Test Fallacy 6: There is one administrator."""
        # Authorized admin succeeds
        self.assertTrue(self.simulator.apply_policy("NodeA", "restart", "Alice"))
        
        # Unauthorized admin fails
        with self.assertRaises(SecurityError):
            self.simulator.apply_policy("NodeA", "restart", "Bob")
            
        # Unknown node fails
        with self.assertRaises(ValueError):
            self.simulator.apply_policy("UnknownNode", "restart", "Admin")

    def test_fallacy_7_transport_cost_is_zero(self):
        """Test Fallacy 7: Transport cost is zero."""
        cost_small = self.simulator.send_message_transport_cost("Hi")
        cost_large = self.simulator.send_message_transport_cost("Hello, this is a much larger message that will take more time to serialize and transmit across the network")
        
        self.assertGreater(cost_small, 0)
        self.assertGreater(cost_large, cost_small)

    def test_fallacy_8_network_is_homogeneous(self):
        """Test Fallacy 8: The network is homogeneous."""
        valid_json = json.dumps({"key": "value"}).encode('utf-8')
        invalid_json = b"xml_data_not_json"
        
        # Expected format parses correctly
        result = self.simulator.parse_message_homogeneous(valid_json, "JSON")
        self.assertEqual(result, {"key": "value"})
        
        # Unexpected format raises an error
        with self.assertRaises(ValueError):
            self.simulator.parse_message_homogeneous(valid_json, "XML")
            
        # Invalid data for the expected format raises an error
        with self.assertRaises(ValueError):
            self.simulator.parse_message_homogeneous(invalid_json, "JSON")

if __name__ == '__main__':
    unittest.main()
