import unittest
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from idempotency_store import IdempotencyStore, process_create_request


class TestIdempotencyStore(unittest.TestCase):
    def test_first_request_records_response(self):
        store = IdempotencyStore()
        response = process_create_request(store, "k1", "order-1")
        self.assertEqual(response, "order-1")

    def test_retry_returns_original_response(self):
        store = IdempotencyStore()
        first = process_create_request(store, "k1", "order-1")
        retry = process_create_request(store, "k1", "order-2")
        self.assertEqual(first, retry)

    def test_concurrent_retries_share_one_response(self):
        store = IdempotencyStore()
        request_count = 8
        start = Barrier(request_count)

        def create_request(index):
            start.wait(timeout=2)
            return process_create_request(store, "same-key", f"order-{index}")

        with ThreadPoolExecutor(max_workers=request_count) as executor:
            responses = list(executor.map(create_request, range(request_count)))

        self.assertEqual(1, len(set(responses)))


if __name__ == '__main__':
    unittest.main()
