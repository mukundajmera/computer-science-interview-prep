# ⚖️ Scoring Rubric: LLM Inference Serving Engine

Use this rubric to evaluate a candidate's system design for an LLM Inference Serving Engine.

## 1. Requirements & Constraints (10%)

| Level | Description |
|---|---|
| **Weak (1-2)** | Ignores latency targets (TTFT vs ITL). Fails to identify GPU memory (VRAM) as the primary constraint. |
| **Okay (3-4)** | Identifies TTFT, ITL, and throughput. Notes memory constraints but doesn't quantify them. |
| **Strong (5)** | Clearly distinguishes between pre-fill (compute-bound) and decode (memory-bound) phases. Understands the trade-off between batch size and latency. |

## 2. Core Architecture & Execution Model (30%)

| Level | Description |
|---|---|
| **Weak (1-2)** | Proposes simple static batching or no batching. Treats the LLM as a black box API without understanding the execution loop. |
| **Okay (3-4)** | Mentions continuous batching or iteration-level scheduling. Describes a basic worker pool but lacks details on tensor parallelism. |
| **Strong (5)** | Designs a robust continuous batching scheduler. Explicitly models the execution loop. Clearly describes how tensor parallelism splits weights across multiple GPUs (Megatron-LM style). |

## 3. KV Cache Management (30%)

| Level | Description |
|---|---|
| **Weak (1-2)** | Ignores KV cache or assumes infinite memory. Allocates contiguous memory based on maximum sequence length. |
| **Okay (3-4)** | Understands KV cache fragmentation. Mentions paging or block-based allocation conceptually. |
| **Strong (5)** | Explicitly designs a Block Manager with block tables (PagedAttention). Discusses prefix caching (RadixTree) to eliminate redundant pre-fill for shared prompts. |

## 4. Latency Optimization & Streaming (15%)

| Level | Description |
|---|---|
| **Weak (1-2)** | Waits for full generation before returning a response. High TTFT. |
| **Okay (3-4)** | Implements streaming (SSE/WebSockets). |
| **Strong (5)** | Implements streaming efficiently. Proposes advanced techniques like speculative decoding or chunked pre-fill to optimize TTFT and ITL further. |

## 5. Resilience & Error Handling (15%)

| Level | Description |
|---|---|
| **Weak (1-2)** | Fails on OOM. No handling of variable request lengths causing memory pressure. |
| **Okay (3-4)** | Evicts requests on OOM but loses progress. |
| **Strong (5)** | Preempts requests gracefully, swaps KV cache to CPU RAM, and restores them later without recomputing the entire prefix. Handles GPU worker failures at the node level. |
