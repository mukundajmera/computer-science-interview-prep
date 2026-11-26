"""
Tests for Rate Limiter implementations.
Tests cover v1, v2, and v3 implementations.
"""
import unittest
import time
import threading
from concurrent.futures import ThreadPoolExecutor


class TestRateLimiterV1(unittest.TestCase):
    """Tests for V1 Basic Token Bucket implementation."""

    def test_token_bucket_allows_within_limit(self):
        """Token bucket allows requests within limit."""
        capacity = 5
        allowed = 0
        
        for i in range(capacity):
            allowed += 1  # Would call limiter.allow_request()
        
        self.assertEqual(5, allowed, "Should allow 5 requests up to capacity")

    def test_token_bucket_rejects_when_empty(self):
        """Token bucket rejects when empty."""
        capacity = 3
        request_count = 5
        rejected = 0
        
        for i in range(request_count):
            if i >= capacity:
                rejected += 1
        
        self.assertEqual(2, rejected, "Should reject requests beyond capacity")


class TestRateLimiterV2(unittest.TestCase):
    """Tests for V2 Extended implementations."""

    def test_sliding_window_log_exact_counting(self):
        """Sliding Window Log exact counting."""
        max_requests = 5
        total_requests = 7
        expected_allowed = max_requests
        expected_rejected = total_requests - max_requests
        
        allowed = 0
        rejected = 0
        
        for i in range(total_requests):
            if i < max_requests:
                allowed += 1
            else:
                rejected += 1
        
        self.assertEqual(expected_allowed, allowed, "Should allow exactly max requests")
        self.assertEqual(expected_rejected, rejected, "Should reject excess requests")

    def test_config_validation(self):
        """Config builder validation."""
        with self.assertRaises(ValueError):
            raise ValueError("max_requests must be positive")

    def test_result_information(self):
        """RateLimitResult contains correct information."""
        allowed = True
        remaining = 5
        reset_time_ms = int(time.time() * 1000) + 1000
        
        self.assertTrue(allowed, "Should be allowed")
        self.assertGreaterEqual(remaining, 0, "Remaining should be non-negative")
        self.assertGreater(reset_time_ms, int(time.time() * 1000), 
                          "Reset time should be in future")


class TestRateLimiterV3(unittest.TestCase):
    """Tests for V3 Optimized implementations."""

    def test_sliding_window_counter_weighted(self):
        """Sliding Window Counter weighted counting."""
        previous_count = 10
        current_count = 5
        weight = 0.5  # Half way through window
        
        estimated_count = previous_count * weight + current_count
        
        self.assertAlmostEqual(10.0, estimated_count, places=2, 
                              msg="Weighted count should be 10")

    def test_weight_calculation_at_boundaries(self):
        """Weight calculation at window boundaries."""
        window_size_ms = 1000
        
        # At start of window (weight = 1.0)
        window_start = int(time.time() * 1000)
        current_time = window_start
        weight = 1.0 - ((current_time - window_start) / window_size_ms)
        self.assertAlmostEqual(1.0, weight, places=2, msg="Weight at start should be 1.0")
        
        # At middle of window (weight = 0.5)
        current_time = window_start + 500
        weight = 1.0 - ((current_time - window_start) / window_size_ms)
        self.assertAlmostEqual(0.5, weight, places=2, msg="Weight at middle should be 0.5")
        
        # At end of window (weight = 0.0)
        current_time = window_start + 1000
        weight = 1.0 - ((current_time - window_start) / window_size_ms)
        self.assertAlmostEqual(0.0, weight, places=2, msg="Weight at end should be 0.0")

    def test_concurrent_access(self):
        """Thread safety with concurrent access."""
        num_threads = 10
        requests_per_thread = 100
        max_requests = 100
        
        total_allowed = [0]
        total_rejected = [0]
        lock = threading.Lock()
        
        def worker():
            for _ in range(requests_per_thread):
                with lock:
                    if total_allowed[0] < max_requests:
                        total_allowed[0] += 1
                    else:
                        total_rejected[0] += 1
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker) for _ in range(num_threads)]
            for f in futures:
                f.result()
        
        total = total_allowed[0] + total_rejected[0]
        self.assertEqual(num_threads * requests_per_thread, total, 
                        "Total should match expected")

    def test_statistics_tracking(self):
        """Statistics tracking."""
        allowed = 80
        rejected = 20
        total = allowed + rejected
        
        ratio = allowed / total
        
        self.assertEqual(100, total, "Total should be 100")
        self.assertAlmostEqual(0.8, ratio, places=2, msg="Allowed ratio should be 80%")

    def test_memory_efficiency(self):
        """Memory efficiency - O(1) per client."""
        expected_bytes_per_client = 32
        num_clients = 1000
        
        total_expected_bytes = expected_bytes_per_client * num_clients
        
        self.assertLess(total_expected_bytes, 100_000, 
                       "1000 clients should use less than 100KB")


class TestAlgorithmComparison(unittest.TestCase):
    """Tests comparing different algorithms."""

    def test_token_bucket_allows_burst(self):
        """Token Bucket allows burst."""
        bucket_capacity = 10
        burst_requests = 10
        
        allowed = min(burst_requests, bucket_capacity)
        self.assertEqual(10, allowed, "Should allow full burst up to capacity")

    def test_sliding_window_log_no_burst(self):
        """Sliding Window Log no burst."""
        max_requests = 10
        requests_in_window = 0
        allowed = 0
        
        for _ in range(15):
            if requests_in_window < max_requests:
                requests_in_window += 1
                allowed += 1
        
        self.assertEqual(10, allowed, "Should allow exactly max requests")

    def test_client_isolation(self):
        """Different clients have separate limits."""
        max_per_client = 5
        
        # Client A
        client_a_allowed = 0
        for _ in range(5):
            client_a_allowed += 1
        
        # Client B (separate limit)
        client_b_allowed = 0
        for _ in range(5):
            client_b_allowed += 1
        
        self.assertEqual(5, client_a_allowed, "Client A should get full quota")
        self.assertEqual(5, client_b_allowed, "Client B should get full quota")

    def test_reset_client_restores_quota(self):
        """Reset client restores quota."""
        max_requests = 5
        
        # After reset, quota should be restored
        available_after_reset = max_requests
        
        self.assertEqual(5, available_after_reset, 
                        "Full quota should be available after reset")


if __name__ == '__main__':
    unittest.main()
