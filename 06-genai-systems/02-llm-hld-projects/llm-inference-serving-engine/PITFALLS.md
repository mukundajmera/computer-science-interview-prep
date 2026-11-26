# 🚨 Common Pitfalls: LLM Inference Serving Engine

When designing an LLM Inference Serving Engine, candidates often make critical mistakes that demonstrate a lack of understanding of hardware limitations and autoregressive execution.

## 1. Static Batching for Variable Length Sequences

**The Pitfall:** Candidates propose standard static batching, where a batch of $N$ requests is formed, and the GPU processes them until all $N$ are complete.
**Why it fails:** LLM outputs are highly variable. If 9 requests generate 10 tokens and 1 request generates 1,000 tokens, the GPU spends 99% of its time processing a single request while the other 9 "slots" are idle, destroying throughput.
**The Fix:** Continuous batching (iteration-level scheduling). Evict requests immediately upon emitting a stop token and insert new requests in the next iteration.

## 2. Contiguous KV Cache Allocation (Memory Fragmentation)

**The Pitfall:** Pre-allocating contiguous VRAM for a request based on the maximum possible context window (e.g., 32k tokens).
**Why it fails:** Most requests do not use the full context window. This leads to massive *internal fragmentation*. Furthermore, as requests finish and new ones start, free memory becomes scattered, leading to *external fragmentation* where a new request cannot be scheduled despite having enough total free VRAM. This artificially limits the batch size and causes Out-Of-Memory (OOM) errors.
**The Fix:** Paged KV cache (PagedAttention). Divide VRAM into fixed-size blocks (e.g., 16 tokens) mapped via a block table, allowing non-contiguous allocation and zero internal/external fragmentation.

## 3. Ignoring the Pre-fill vs. Decode Bottlenecks

**The Pitfall:** Treating prompt processing (pre-fill) and token generation (decode) as having identical performance characteristics.
**Why it fails:** Pre-fill computes the attention over the entire prompt in parallel; it is compute-bound (FLOP-bound). Decode computes attention token-by-token, loading the entire model weights and KV cache for each step; it is memory-bandwidth bound. Mixing them naively causes latency spikes.
**The Fix:** The scheduler must explicitly manage the transition. Chunked pre-fill can split a long prompt across multiple iterations to avoid stalling the decode iterations of other concurrent requests.

## 4. Recomputing the KV Cache on Preemption

**The Pitfall:** If the system runs out of VRAM (e.g., because sequences generated longer than expected), the candidate proposes terminating or evicting a request and starting it over later.
**Why it fails:** Re-running the pre-fill phase for a long prompt wastes massive amounts of compute and severely impacts P99 latency.
**The Fix:** Swap the preempted request's KV cache blocks from GPU VRAM to CPU RAM over PCIe. When VRAM frees up, swap the blocks back and resume generation without recomputing the context.

## 5. Single-GPU Assumption for Large Models

**The Pitfall:** Designing the system assuming a single GPU can hold the model.
**Why it fails:** A 70B parameter model in FP16 requires ~140GB just for weights. An 80GB A100 cannot hold it, let alone the KV cache.
**The Fix:** Implement distributed execution using Tensor Parallelism (e.g., Megatron-LM) across multiple GPUs connected via high-bandwidth interconnects (NVLink). Pipeline parallelism is also an option but introduces bubbles (idle time) that are harder to optimize for inference.
