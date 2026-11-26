import unittest
import sys
import os

# Add the parent directory to the path so we can import v1_basic
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from importlib import import_module
cdn_simulator = import_module('v1-basic.cdn_simulator')

class TestCdnSimulator(unittest.TestCase):

    def test_normal_hit(self):
        origin = cdn_simulator.CustomerOrigin()
        origin.put("/images/logo.png", "binary_data_123")

        shield = cdn_simulator.OriginShield(origin)
        edge = cdn_simulator.EdgeNode(shield)

        # Miss -> hits origin
        result1 = edge.fetch("/images/logo.png")
        self.assertEqual(result1, "binary_data_123")
        self.assertEqual(origin.fetch_count, 1)

        # Hit -> hits edge cache
        result2 = edge.fetch("/images/logo.png")
        self.assertEqual(result2, "binary_data_123")
        self.assertEqual(edge.cache_hit_count, 1)
        self.assertEqual(origin.fetch_count, 1)  # Origin not hit again

    def test_thundering_herd_coalescing(self):
        origin = cdn_simulator.CustomerOrigin()
        origin.put("/videos/viral.mp4", "video_data_999")

        shield = cdn_simulator.OriginShield(origin)
        edge = cdn_simulator.EdgeNode(shield)

        results = []
        # Simulate 10,000 concurrent requests hitting the edge and then the shield
        edge.fetch_batch("/videos/viral.mp4", 10000, results)

        self.assertEqual(len(results), 10000)
        for res in results:
            self.assertEqual(res, "video_data_999")

        # Thundering herd invariant: Origin is protected by request coalescing
        # 10,000 requests to the shield should result in exactly 1 request to the Origin
        self.assertEqual(origin.fetch_count, 1)
        self.assertEqual(shield.fetch_count, 10000)

if __name__ == '__main__':
    unittest.main()
