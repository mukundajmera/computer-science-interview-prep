import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mvcc.mvcc_transaction_engine import MvccTransactionEngine, IsolationLevel

class TestMvccTransactionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = MvccTransactionEngine()

    def test_dirty_read_prevention(self):
        tx1 = self.engine.begin(IsolationLevel.READ_COMMITTED)
        self.engine.write(tx1, "k1", "v1")
        
        tx2 = self.engine.begin(IsolationLevel.READ_COMMITTED)
        val = self.engine.read(tx2, "k1")
        
        self.assertIsNone(val, "Transaction 2 should not read uncommitted writes of Transaction 1")
        
        self.engine.commit(tx1)
        val2 = self.engine.read(tx2, "k1")
        self.assertEqual(val2, "v1", "Transaction 2 should read committed writes after tx1 commits (READ_COMMITTED)")

    def test_repeatable_read_snapshot_isolation(self):
        # Init
        tx0 = self.engine.begin()
        self.engine.write(tx0, "k1", "v0")
        self.engine.commit(tx0)

        tx1 = self.engine.begin(IsolationLevel.SNAPSHOT_ISOLATION)
        val1 = self.engine.read(tx1, "k1")
        self.assertEqual(val1, "v0")

        tx2 = self.engine.begin(IsolationLevel.READ_COMMITTED)
        self.engine.write(tx2, "k1", "v2")
        self.engine.commit(tx2)

        val2 = self.engine.read(tx1, "k1")
        self.assertEqual(val2, "v0", "Snapshot Isolation should provide repeatable reads")

    def test_first_committer_wins(self):
        # Init
        tx0 = self.engine.begin()
        self.engine.write(tx0, "k1", "v0")
        self.engine.commit(tx0)

        tx1 = self.engine.begin(IsolationLevel.SNAPSHOT_ISOLATION)
        tx2 = self.engine.begin(IsolationLevel.SNAPSHOT_ISOLATION)

        self.engine.write(tx1, "k1", "v1")
        self.engine.write(tx2, "k1", "v2")

        res1 = self.engine.commit(tx1)
        self.assertTrue(res1)

        res2 = self.engine.commit(tx2)
        self.assertFalse(res2, "Second committer should fail under first-committer-wins rule")
        
        tx3 = self.engine.begin()
        self.assertEqual(self.engine.read(tx3, "k1"), "v1")

    def test_write_skew_reproduction(self):
        """
        Demonstrates write skew vulnerability under Snapshot Isolation.
        E.g., two doctors on call. At least one must be on call.
        """
        # Init
        tx0 = self.engine.begin()
        self.engine.write(tx0, "doc1", "on_call")
        self.engine.write(tx0, "doc2", "on_call")
        self.engine.commit(tx0)

        tx1 = self.engine.begin(IsolationLevel.SNAPSHOT_ISOLATION)
        tx2 = self.engine.begin(IsolationLevel.SNAPSHOT_ISOLATION)

        # tx1 checks doc2
        doc2_status = self.engine.read(tx1, "doc2")
        if doc2_status == "on_call":
            self.engine.write(tx1, "doc1", "off_call")

        # tx2 checks doc1
        doc1_status = self.engine.read(tx2, "doc1")
        if doc1_status == "on_call":
            self.engine.write(tx2, "doc2", "off_call")

        # Both commit successfully because they write to different keys
        res1 = self.engine.commit(tx1)
        res2 = self.engine.commit(tx2)

        self.assertTrue(res1)
        self.assertTrue(res2)

        # Final state check
        tx3 = self.engine.begin()
        self.assertEqual(self.engine.read(tx3, "doc1"), "off_call")
        self.assertEqual(self.engine.read(tx3, "doc2"), "off_call")
        # Invariant (at least one doctor on call) is violated, demonstrating Write Skew

if __name__ == '__main__':
    unittest.main()
