# 🛠️ Approach: LLM Inference Serving Engine

Designing an LLM inference serving engine requires deep understanding of how transformer models execute autoregressively and where the primary bottlenecks exist. The overarching goal is to achieve high throughput without sacrificing latency (TTFT and ITL).

## Core Challenges

1.  **Memory Wall:** Generating a token requires loading the model weights and the KV cache for the context into the GPU computing cores. The time taken is dominated by memory bandwidth, not compute (FLOPs).
2.  **Variable Sequence Lengths:** Requests have different input lengths and generate different output lengths, making static batching inefficient.
3.  **KV Cache Fragmentation:** Naively pre-allocating contiguous memory for the maximum possible sequence length leads to severe internal and external memory fragmentation, wasting VRAM and limiting batch sizes.

## Key Design Patterns

### 1. Iteration-Level Continuous Batching

**Concept & Citation:** Continuous Batching (Yu et al., 2022, *Orca: A Distributed Serving System for Transformer-Based Generative Models*).

**The Problem:** Traditional static batching waits for all requests in a batch to finish before starting a new batch. Given variable output lengths, early-finishing requests stall, wasting compute cycles while waiting for longer requests.

**The Solution:** Continuous Batching operates at the iteration level (per token generation). 
-   When a request finishes generating its final token, it is immediately evicted from the batch.
-   A new request from the waiting queue is dynamically inserted into the active batch.
-   This ensures the batch size remains consistently high, maximizing GPU utilization. **Assumption:** Overhead of scheduling and dynamic batch construction per iteration is negligible compared to the forward pass execution time.

### 2. Virtual Memory Paging for KV Cache (PagedAttention)

**Concept & Citation:** PagedAttention (Kwon et al., 2023, *Efficient Memory Management for Large Language Model Serving with PagedAttention*).

**The Problem:** The KV cache stores intermediate tensor states for past tokens to avoid recomputing them. If allocated contiguously per request based on maximum length, fragmentation limits the number of requests that can fit in VRAM.

**The Solution:** Inspired by OS virtual memory, PagedAttention divides the KV cache into fixed-size blocks (e.g., 16 or 32 tokens per block).
-   Blocks do not need to be contiguous in physical VRAM.
-   A Block Manager maintains a block table mapping logical tokens to physical blocks.
-   Memory is allocated dynamically as new tokens are generated.
-   This nearly eliminates memory fragmentation, allowing a much larger batch size to fit in the same GPU memory. **Assumption:** The overhead of scattered memory access (gather operations) is hidden by the high memory bandwidth and compute intensity of the decode phase.

### 3. RadixTree-based Prefix Caching

**Concept & Citation:** RadixAttention (Zheng et al., 2023, *Efficient Routing for LLM Serving* / SGLang).

**The Problem:** Many requests share identical prefixes (e.g., system prompts, few-shot examples, or document context). Recomputing the KV cache for these shared prefixes wastes compute and time.

**The Solution:** Implement a RadixTree to manage the KV cache blocks.
-   Nodes in the tree represent sequences of tokens.
-   When a new request arrives, the engine matches its prefix against the RadixTree.
-   If a match is found, the physical KV cache blocks for that prefix are reused (using explicit reference counts, `refcounts`, to track concurrent access).
-   This dramatically reduces Time To First Token (TTFT) for requests with shared contexts. **Assumption:** The frequency of shared prefixes is high enough to justify the memory overhead of maintaining the RadixTree data structure.

### 4. Distributed Execution (Tensor Parallelism)

**Concept & Citation:** Megatron-LM (Shoeybi et al., 2019, *Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism*).

**The Problem:** A 70B parameter model requires ~140GB of VRAM (at FP16 precision), exceeding the capacity of a single GPU (e.g., 80GB A100 (NVIDIA, 2020)).

**The Solution:** Tensor Parallelism (e.g., Megatron-LM).
-   Model weights and computation are partitioned across multiple GPUs (workers) within a single node connected via NVLink.
-   Each GPU computes a portion of the attention and feed-forward networks.
-   All-reduce operations synchronize the intermediate activations between GPUs.
-   The Scheduler coordinates execution across all workers.

### 5. Speculative Decoding (Draft Model Loop)

**Concept & Citation:** Speculative Decoding (Leviathan et al., 2023, *Fast Inference from Transformers via Speculative Decoding*).

**The Problem:** Autoregressive generation is inherently sequential.

**The Solution:** Speculative Decoding uses a smaller, faster "draft" model to predict multiple future tokens.
-   The draft model generates a sequence of tokens (e.g., 5 tokens) quickly.
-   The larger "target" model evaluates all 5 drafted tokens in a single parallel forward pass.
-   If the target model agrees with the drafted tokens, they are accepted, effectively generating multiple tokens in one step.
-   If it disagrees, the sequence is corrected. This significantly reduces Inter-Token Latency.

### 6. Chunked Prefill

**Concept & Citation:** Chunked Prefill / Sarathi (Agrawal et al., 2024, *Sarathi: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills*).

**The Problem:** The prefill phase for a long prompt requires significant compute and stalls the memory-bound decode iterations of active requests, causing spikes in Inter-Token Latency (ITL).

**The Solution:** The prompt is split into smaller chunks (e.g., 512 tokens). Each scheduling iteration processes one prefill chunk alongside the decode tokens for active requests.
-   **Assumption:** Attention can be computed iteratively over chunks without losing mathematical equivalence. This keeps streaming latency smooth and predictable.

### 7. Preemption & Swap

**Concept & Citation:** KV Cache Swapping (Kwon et al., 2023, *Efficient Memory Management for Large Language Model Serving with PagedAttention* / vLLM).

**The Problem:** Because output sequence lengths are unpredictable, continuous batching can overcommit VRAM if multiple requests generate unexpectedly long responses.

**The Solution:** When VRAM is exhausted, the scheduler preempts a lower-priority active request. Its physical KV cache blocks are swapped to CPU RAM. When VRAM frees up, the blocks are swapped back, and the request resumes.
-   **Assumption:** CPU-to-GPU PCIe bandwidth is sufficient to hide the latency of swapping, or swapping is rare enough that it does not significantly degrade overall throughput.

