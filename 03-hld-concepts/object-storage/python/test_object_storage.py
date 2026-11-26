import unittest
from v1_checksummed import V1ChecksummedStore
from v2_chunked_replicated import V2ChunkedReplicatedStore
from v3_xor_parity import V3XorParityStore

class TestObjectStorage(unittest.TestCase):

    def test_v1_checksum_rot(self):
        store = V1ChecksummedStore()
        store.put("doc.txt", b"Hello World")
        self.assertEqual(store.get("doc.txt"), b"Hello World")
        
        # Simulate Bit Rot
        store.corrupt_data_for_testing("doc.txt")
        with self.assertRaises(ValueError) as context:
            store.get("doc.txt")
        self.assertIn("Bit rot detected", str(context.exception))

    def test_v2_replication_survives_failure(self):
        store = V2ChunkedReplicatedStore(chunk_size=4, replication_factor=3)
        data = b"Large Data Payload For Testing"
        store.put("video.mp4", data)
        
        # Original read
        self.assertEqual(store.get("video.mp4"), data)
        
        # Wipe node 0 and node 1 (replication factor 3 should survive 2 failures)
        store.simulate_node_failure(0)
        store.simulate_node_failure(1)
        
        # Should still read successfully from replicas
        self.assertEqual(store.get("video.mp4"), data)

    def test_v3_parity_recovery(self):
        store = V3XorParityStore(data_chunks_k=4)
        data = b"ErasureCodingIsMagic!!" # 22 bytes
        store.put("backup.tar", data)
        
        # Normal read
        self.assertEqual(store.get("backup.tar"), data)
        
        # Simulate node 1 failure (a data node)
        store.simulate_node_failure(1)
        
        # Degraded read should reconstruct using XOR
        self.assertEqual(store.get("backup.tar"), data)
        
        # Scrub and repair
        self.assertTrue(store.scrub_and_repair("backup.tar"))
        
        # After repair, node 1 should have the chunk again
        self.assertIsNotNone(store.nodes[1].get("backup.tar_c1"))
        
        # Simulate node 4 failure (the parity node)
        store.simulate_node_failure(4)
        self.assertEqual(store.get("backup.tar"), data) # Can still read data normally

if __name__ == '__main__':
    unittest.main()
