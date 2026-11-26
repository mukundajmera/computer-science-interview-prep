# LLM Inference Serving Engines

The rapid scaling of Large Language Models (LLMs) has revolutionized artificial intelligence, providing unprecedented capabilities in natural language understanding, reasoning, and generation. However, serving these massive models in production environments presents significant systems engineering challenges. Specifically, generating text auto-regressively token by token is highly memory-bound and latency-sensitive. A key component of modern LLM inference serving is the KV cache, an essential optimization used to avoid redundant computation during the decoding phase. As inference scales, managing this KV cache efficiently becomes a dominant bottleneck. This document explores the fundamental math behind the KV cache, the evolution from static batching to continuous batching, and the breakthrough memory management technique introduced by vLLM known as PagedAttention.

## KV Cache Math

In standard Transformer architectures, text generation involves a prefill phase (processing the entire prompt simultaneously) followed by a decoding phase (generating new tokens one by one). During the decoding phase, calculating the attention score for a newly generated token requires the Keys (K) and Values (V) of all previous tokens. Rather than recomputing these tensors from scratch at every step, inference engines store them in a Key-Value cache, commonly referred to as the KV cache. 

The memory footprint of the KV cache is substantial and scales linearly with the sequence length. To estimate the memory consumption for a single token's KV cache, we use the following equation:

$$ \text{Memory per Token (Bytes)} = 2 \times \text{Layers} \times \text{Heads} \times \text{Head Dimension} \times \text{Precision (Bytes)} $$

Here, the factor of 2 accounts for both the Key and Value matrices. For a large model like LLaMA 2 70B, which has 80 layers, 64 attention heads, and a head dimension of 128, stored in 16-bit precision (2 bytes), the KV cache size for a single token per request is:

$2 \times 80 \times 64 \times 128 \times 2 = 2.6 \text{ MB per token}$

If we process a batch of 128 requests with an average context length of 2,048 tokens, the KV cache alone demands approximately 681 GB of GPU memory, significantly outstripping the memory capacity of even multiple high-end GPUs like the NVIDIA A100 (which offers 80GB each). Efficiently managing this memory is critical to increasing batch sizes and maximizing GPU utilization.

## Continuous Batching

Early inference systems relied on static batching, where a fixed number of requests are grouped together. In static batching, the batch must wait for the longest request to finish generating all its tokens before the batch can be marked as complete and a new batch can start. This results in significant GPU underutilization, as shorter requests finish early but occupy resources while waiting for the longest request to complete.

To address this inefficiency, ORCA introduced continuous batching (also known as iteration-level scheduling or in-flight batching). Continuous batching dynamically inserts new requests into a running batch as soon as an active request completes. At every iteration (i.e., at every token generation step), the system evaluates the state of all requests. Completed requests are evicted, and newly arrived requests are injected. This fine-grained scheduling allows the system to sustain a high and constant batch size over time, dramatically improving throughput and GPU utilization without significantly impacting the latency of individual requests.

## PagedAttention and vLLM

While continuous batching improves compute utilization, traditional KV cache memory allocation still suffers from severe fragmentation. Standard systems pre-allocate a contiguous block of memory based on the maximum possible sequence length of a request. Because the actual length of the generated output is unknown a priori, this leads to significant internal fragmentation (reserved memory that is never used) and external fragmentation (memory holes between contiguous blocks). In practice, memory utilization in these systems can be as low as 20% to 40%.

To solve this, the vLLM engine introduced PagedAttention, drawing inspiration from virtual memory paging in operating systems. Instead of storing the KV cache for a sequence in a single contiguous memory block, PagedAttention partitions the sequence into smaller, fixed-size blocks (e.g., blocks containing the KV vectors for 16 or 32 tokens). These blocks can be allocated non-contiguously in the physical GPU memory. A centralized block table tracks the mapping between logical blocks (the sequence's tokens) and physical memory blocks.

During attention computation, the PagedAttention algorithm fetches the necessary K and V vectors by looking up their physical locations via the block table. This approach entirely eliminates internal fragmentation, as memory is allocated incrementally on demand (one block at a time). It also mitigates external fragmentation because all blocks are of a fixed, uniform size. Consequently, PagedAttention allows vLLM to achieve near-optimal memory utilization (often exceeding 90%), enabling much larger batch sizes and significantly improving the overall throughput of LLM serving infrastructure. Furthermore, it naturally supports memory sharing for complex decoding techniques, such as beam search and parallel sampling, by allowing multiple sequences to share identical prefix blocks.
