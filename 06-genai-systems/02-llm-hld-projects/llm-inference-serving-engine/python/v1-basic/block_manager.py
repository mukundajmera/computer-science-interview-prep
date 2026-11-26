"""
Educational Simulator: KV Cache Block Manager
=============================================
This module simulates a paged KV cache block manager as used in modern LLM serving engines.

What is simulated:
- Fixed-size token block allocation and freeing.
- Logical-to-physical mapping of tokens to blocks for each sequence.
- Optional prefix block sharing via reference counting (useful for prompt sharing).
- Out-of-memory handling when blocks are exhausted.

What is NOT simulated:
- Actual GPU kernels or real tensor data.
- Production throughput or precise serving performance.
- Swapping latency (moving blocks to/from CPU/GPU memory).
- Scheduler optimality.

Note: No assertion equates CPU simulation with GPU serving performance. This is purely a deterministic CPU reference for capacity and state transitions.
"""

from typing import Dict, List, Optional

class OutOfMemoryError(Exception):
    """Raised when there are not enough free blocks available."""
    pass

class BlockManager:
    def __init__(self, num_blocks: int, block_size: int):
        self.num_blocks = num_blocks
        self.block_size = block_size
        
        # Free blocks
        self.free_blocks: List[int] = list(range(num_blocks))
        
        # Block ref counts: physical block ID -> count
        self.ref_counts: Dict[int, int] = {i: 0 for i in range(num_blocks)}

    def can_allocate(self, num_blocks_needed: int) -> bool:
        """Check if enough free blocks are available."""
        return len(self.free_blocks) >= num_blocks_needed

    def allocate(self) -> int:
        """Allocate a single block and return its physical block ID."""
        if not self.free_blocks:
            raise OutOfMemoryError("No free blocks available.")
        
        block_id = self.free_blocks.pop(0)
        self.ref_counts[block_id] = 1
        return block_id

    def free(self, block_id: int) -> None:
        """Decrement reference count and free the block if it reaches zero."""
        if block_id not in self.ref_counts or self.ref_counts[block_id] == 0:
            return  # Or raise an error
            
        self.ref_counts[block_id] -= 1
        if self.ref_counts[block_id] == 0:
            self.free_blocks.append(block_id)

    def acquire_shared(self, block_id: int) -> None:
        """Increment reference count for a shared block (e.g., shared prefix)."""
        if block_id not in self.ref_counts or self.ref_counts[block_id] == 0:
            raise ValueError(f"Cannot share block {block_id} which is not allocated.")
        self.ref_counts[block_id] += 1
