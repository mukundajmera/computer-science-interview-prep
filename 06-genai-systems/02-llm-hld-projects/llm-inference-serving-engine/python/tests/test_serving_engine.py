"""
Educational Simulator Tests
===========================
Tests for the deterministic CPU reference simulator for paged KV allocation and continuous batching.

Note: No assertion equates CPU simulation with GPU serving performance. This is purely a deterministic CPU reference for capacity and state transitions.
"""

import sys
import os
import unittest

# Temporarily manipulate sys.path to enable standard-looking imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(parent_dir, "v1-basic"))

from block_manager import BlockManager, OutOfMemoryError
from continuous_batcher import Request, ContinuousBatcher

sys.path.pop(0)

class TestServingEngine(unittest.TestCase):
    def test_block_allocation_and_exhaustion(self):
        bm = BlockManager(num_blocks=2, block_size=16)
        self.assertTrue(bm.can_allocate(2))
        self.assertFalse(bm.can_allocate(3))
        
        b1 = bm.allocate()
        b2 = bm.allocate()
        
        with self.assertRaises(OutOfMemoryError):
            bm.allocate()
            
        bm.free(b1)
        b3 = bm.allocate()
        self.assertEqual(b3, b1)

    def test_shared_prefix_refcount(self):
        bm = BlockManager(num_blocks=5, block_size=16)
        b1 = bm.allocate()
        
        # Simulate sharing the prefix block
        bm.acquire_shared(b1)
        
        # First free shouldn't release to free_blocks
        bm.free(b1)
        self.assertEqual(len(bm.free_blocks), 4)
        
        # Second free should release it
        bm.free(b1)
        self.assertEqual(len(bm.free_blocks), 5)

    def test_admission_and_completion(self):
        bm = BlockManager(num_blocks=10, block_size=16)
        batcher = ContinuousBatcher(bm)
        
        # Prompt is 10 tokens (1 block), max output 20 tokens. Total max = 30 (2 blocks)
        req1 = Request("r1", prompt_tokens=10, max_output_tokens=20)
        batcher.add_request(req1)
        
        self.assertEqual(len(batcher.waiting_queue), 1)
        self.assertEqual(len(batcher.running_queue), 0)
        
        # Step 1: Admits request (1 block allocated)
        batcher.step()
        self.assertEqual(len(batcher.waiting_queue), 0)
        self.assertEqual(len(batcher.running_queue), 1)
        self.assertEqual(req1.generated_tokens, 1)
        self.assertEqual(len(bm.free_blocks), 9) # 1 block for prompt+first token
        
        # Generate until completion (19 more steps)
        for _ in range(19):
            batcher.step()
            
        self.assertTrue(req1.completed)
        # Since completed, step should have cleaned it up
        self.assertEqual(len(batcher.running_queue), 0)
        # Output token 20 pushed total tokens to 30, which fits in 2 blocks.
        # But since it's completed and cleaned up, blocks should be fully freed.
        self.assertEqual(len(bm.free_blocks), 10)

    def test_preemption_policy(self):
        # Only 2 blocks available.
        bm = BlockManager(num_blocks=2, block_size=16)
        batcher = ContinuousBatcher(bm)
        
        # Req 1 needs 1 block for prompt (10 tokens), and will need 1 more for output (up to 30 total)
        req1 = Request("r1", prompt_tokens=10, max_output_tokens=20)
        batcher.add_request(req1)
        
        # Req 2 needs 1 block for prompt (10 tokens), and will need 1 more for output (up to 30 total)
        req2 = Request("r2", prompt_tokens=10, max_output_tokens=20)
        batcher.add_request(req2)
        
        # Step 1: Admits both requests (each takes 1 block)
        batcher.step()
        
        self.assertEqual(len(batcher.running_queue), 2)
        self.assertEqual(len(bm.free_blocks), 0)
        
        # Step 2-6: Both requests generate up to token 6 (total 16 tokens each -> 1 block)
        for _ in range(5):
            batcher.step()
            
        self.assertEqual(req1.generated_tokens, 6)
        self.assertEqual(req2.generated_tokens, 6)
        self.assertEqual(len(bm.free_blocks), 0)
        
        # Step 7: Generating token 7 puts total at 17 tokens each. They each need a 2nd block!
        # Req 1 will try to allocate and fail, so it gets preempted.
        # Req 2 will then try to allocate, and since Req 1 was preempted and freed its 1 block, Req 2 will succeed.
        batcher.step()
        
        # One should be preempted (in waiting queue), the other still running
        self.assertEqual(len(batcher.waiting_queue), 1)
        self.assertEqual(len(batcher.running_queue), 1)
        
        preempted_req = batcher.waiting_queue[0]
        running_req = batcher.running_queue[0]
        
        self.assertEqual(preempted_req.generated_tokens, 0) # Preempted and reset
        self.assertEqual(running_req.generated_tokens, 7) # Successfully generated 7th token
        
        # 2 total blocks: running req uses 2 blocks now (17 tokens > 16)
        self.assertEqual(len(bm.free_blocks), 0)

if __name__ == '__main__':
    unittest.main()
