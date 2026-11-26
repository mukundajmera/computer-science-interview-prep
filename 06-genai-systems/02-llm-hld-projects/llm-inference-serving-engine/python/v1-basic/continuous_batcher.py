"""
Educational Simulator: Continuous Batcher
=========================================
This module simulates a continuous batching scheduler for LLM inference.

What is simulated:
- Iteration-level token generation.
- Dynamic request admission based on KV cache capacity.
- Preemption and recomputation policies.

What is NOT simulated:
- Actual GPU kernels or real tensor data.
- Production throughput or precise serving performance.
- Swapping latency.

Note: No assertion equates CPU simulation with GPU serving performance. This is purely a deterministic CPU reference for capacity and state transitions.
"""

from typing import List, Optional
import math
from block_manager import BlockManager, OutOfMemoryError

class Request:
    def __init__(self, request_id: str, prompt_tokens: int, max_output_tokens: int):
        self.request_id = request_id
        self.prompt_tokens = prompt_tokens
        self.max_output_tokens = max_output_tokens
        
        # Generation state
        self.generated_tokens = 0
        self.logical_blocks: List[int] = [] # mapped to physical block IDs
        self.completed = False

class ContinuousBatcher:
    def __init__(self, block_manager: BlockManager):
        self.block_manager = block_manager
        self.waiting_queue: List[Request] = []
        self.running_queue: List[Request] = []

    def add_request(self, req: Request):
        self.waiting_queue.append(req)

    def step(self):
        """
        Advances the batcher by one token generation step.
        - Admits waiting requests if blocks are available.
        - Generates one token for each running request.
        - Frees blocks for completed requests.
        - Preempts (aborts/recomputes) if memory is exhausted during generation.
        """
        self._admit_requests()
        self._generate_step()
        self._cleanup_completed()

    def _admit_requests(self):
        """Admit requests from the waiting queue if prompt blocks are available."""
        # A simple admission policy: admit as many as we can fit their prompt
        admitted = []
        for req in self.waiting_queue:
            num_blocks_needed = math.ceil(req.prompt_tokens / self.block_manager.block_size)
            
            if self.block_manager.can_allocate(num_blocks_needed):
                try:
                    for _ in range(num_blocks_needed):
                        block_id = self.block_manager.allocate()
                        req.logical_blocks.append(block_id)
                    self.running_queue.append(req)
                    admitted.append(req)
                except OutOfMemoryError:
                    break # Should not happen due to can_allocate check
            else:
                # In this simple policy, if the head of the queue can't be admitted, we stop
                break
                
        for req in admitted:
            self.waiting_queue.remove(req)

    def _generate_step(self):
        """Advance each running request by one token, allocating blocks if needed."""
        # We need to iterate over a copy of running_queue since we might remove from it
        for req in list(self.running_queue):
            if req.completed:
                continue
                
            total_tokens = req.prompt_tokens + req.generated_tokens + 1
            blocks_needed = math.ceil(total_tokens / self.block_manager.block_size)
            
            if blocks_needed > len(req.logical_blocks):
                try:
                    block_id = self.block_manager.allocate()
                    req.logical_blocks.append(block_id)
                except OutOfMemoryError:
                    # Preempt immediately to free blocks for subsequent requests
                    self._preempt(req)
                    continue
            
            # Successfully generated 1 token
            req.generated_tokens += 1
            
            if req.generated_tokens >= req.max_output_tokens:
                req.completed = True

    def _preempt(self, req: Request):
        """Preempt a request by freeing its blocks and resetting its state, returning to waiting."""
        self.running_queue.remove(req)
        for block_id in req.logical_blocks:
            self.block_manager.free(block_id)
        
        # Reset generation state for "recompute" policy
        req.generated_tokens = 0
        req.logical_blocks = []
        
        # Put back at the front of the waiting queue
        self.waiting_queue.insert(0, req)

    def _cleanup_completed(self):
        """Free blocks for completed requests and remove them from running queue."""
        completed_reqs = [r for r in self.running_queue if r.completed]
        
        for req in completed_reqs:
            for block_id in req.logical_blocks:
                self.block_manager.free(block_id)
            req.logical_blocks = []
            self.running_queue.remove(req)
