import os
import sys
import time
import threading
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))
from write_batcher import WriteBatcher

class TestWriteBatcher(unittest.TestCase):

    def test_flush_by_batch_size(self):
        committed_batches = []
        latch = threading.Event()

        def commit_batch(batch):
            committed_batches.append(batch)
            latch.set()

        with WriteBatcher(capacity=10, batch_size_threshold=3, max_wait_duration_ms=5000, batch_committer=commit_batch) as batcher:
            self.assertTrue(batcher.write("item1"))
            self.assertTrue(batcher.write("item2"))

            # Should not have flushed yet
            self.assertEqual(len(committed_batches), 0)

            self.assertTrue(batcher.write("item3"))

            # Wait for flush
            latch.wait(timeout=2.0)
            self.assertEqual(len(committed_batches), 1)
            self.assertEqual(len(committed_batches[0]), 3)
            self.assertIn("item1", committed_batches[0])
            self.assertIn("item2", committed_batches[0])
            self.assertIn("item3", committed_batches[0])

    def test_flush_by_wait_duration(self):
        committed_batches = []
        latch = threading.Event()

        def commit_batch(batch):
            committed_batches.append(batch)
            latch.set()

        with WriteBatcher(capacity=10, batch_size_threshold=5, max_wait_duration_ms=200, batch_committer=commit_batch) as batcher:
            self.assertTrue(batcher.write("item1"))
            self.assertTrue(batcher.write("item2"))

            # Should not have flushed yet immediately
            self.assertEqual(len(committed_batches), 0)

            # Wait for duration to pass
            latch.wait(timeout=2.0)
            self.assertEqual(len(committed_batches), 1)
            self.assertEqual(len(committed_batches[0]), 2)

    def test_backpressure_rejection(self):
        commit_count = [0]

        def commit_batch(batch):
            time.sleep(0.1)  # slow consumer
            commit_count[0] += 1

        with WriteBatcher(capacity=2, batch_size_threshold=2, max_wait_duration_ms=5000, batch_committer=commit_batch) as batcher:
            self.assertTrue(batcher.write("item1"))
            self.assertTrue(batcher.write("item2"))

            batcher.write("item3")

            rejected = not batcher.write("item4") or not batcher.write("item5") or not batcher.write("item6")
            self.assertTrue(rejected)

    def test_flush_on_close(self):
        committed_batches = []

        def commit_batch(batch):
            committed_batches.append(batch)

        batcher = WriteBatcher(capacity=10, batch_size_threshold=5, max_wait_duration_ms=5000, batch_committer=commit_batch)

        self.assertTrue(batcher.write("item1"))
        self.assertTrue(batcher.write("item2"))

        batcher.close()

        self.assertEqual(len(committed_batches), 1)
        self.assertEqual(len(committed_batches[0]), 2)

        with self.assertRaises(RuntimeError):
            batcher.write("item3")

if __name__ == '__main__':
    unittest.main()
