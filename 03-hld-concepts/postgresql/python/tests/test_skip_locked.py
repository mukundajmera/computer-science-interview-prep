import sys, os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-expert'))
from skip_locked import SkipLockedQueue

class TestSkipLocked(unittest.TestCase):
    def test_queue(self):
        q = SkipLockedQueue()
        q.enqueue(1)
        self.assertEqual(q.dequeue(), 1)
