# 🏗️ System Design: LLM Inference Serving Engine

## 1. High-Level Architecture

The LLM Inference Serving Engine consists of the following primary components:

1.  **API Gateway / Router:** Handles incoming HTTP/gRPC requests, performs authentication, tokenizes the input, and routes to the appropriate model scheduler.
2.  **Scheduler (Continuous Batching):** Manages the queue of requests, decides which requests participate in the next forward pass, and orchestrates execution.
3.  **KV Cache Block Manager:** Allocates and manages physical KV cache blocks in GPU VRAM and CPU RAM, implementing the PagedAttention logic and prefix caching.
4.  **Worker Pool (Execution Engine):** A group of GPUs executing the model weights using Tensor Parallelism.
5.  **Streaming Handler:** Manages the Server-Sent Events (SSE) connections back to the clients.

## 2. Component Deep Dives

### 2.1 Model Gateway & Tokenization
The API Gateway acts as the entry point. When a request arrives, it is immediately tokenized. This is done on the CPU before the request enters the GPU scheduling queue. Tokenization is fast but necessary to know the sequence length for KV cache allocation planning.

### 2.2 Scheduler & KV Cache Block Manager
The Scheduler is the brain of the engine. It operates a Continuous Batching loop (Yu et al., 2022):
-   **Pre-fill Phase (Concept per Pope et al., 2022):** When a new request starts, its entire prompt is processed in one pass to generate the initial KV cache and the first token. This is compute-bound. **Assumption:** GPU streaming multiprocessors (SMs) are fully saturated with GEMM operations during this phase.
-   **Decode Phase (Concept per Pope et al., 2022):** For ongoing requests, one token is generated at a time. This is memory-bound. **Assumption:** Total elapsed time for iteration is constrained primarily by VRAM bandwidth reading weights and KV cache, rather than raw ALUs compute speed.

The Scheduler maintains two queues: `Waiting` and `Running`.
In each iteration, the Scheduler:
1. Checks available physical KV cache blocks via the Block Manager.
2. Selects requests from the `Running` queue.
3. If space permits, admits requests from the `Waiting` queue (prioritizing based on a policy, e.g., FCFS or shortest-job-first if lengths are known).
4. Issues the execution command to the Worker Pool.

**KV Cache Management (PagedAttention, Kwon et al., 2023):**
The Block Manager divides VRAM into blocks (e.g., 16 tokens). It maintains a Block Table for each request. When a sequence grows beyond its current block, a new physical block is dynamically allocated. If VRAM is full, the Scheduler can preempt lower-priority requests, swapping their KV cache to CPU RAM, and restoring it later.

### 2.3 Distributed Tensor Parallel Workers (Megatron-LM style) (Shoeybi et al., 2019)
For models like Llama-3-70B, weights are sharded across multiple GPUs (e.g., 8x GPUs). 
-   **Column Parallelism:** The first linear layer is split along the output dimension. Each GPU computes a portion of the intermediate activations.
-   **Row Parallelism:** The second linear layer is split along the input dimension. The results are aggregated using an `AllReduce` operation over NVLink.
-   The Scheduler runs on the CPU and broadcasts the batch information (input tokens, block tables) to all workers. The workers execute the forward pass synchronously.

### 2.4 Streaming Token SSE Response Handler
As the worker pool generates tokens in the decode phase, they are immediately detokenized and pushed to an asynchronous message queue or channel. The Streaming Handler reads from this channel and sends Server-Sent Events (SSE) chunks back to the client, minimizing the Time To First Token (TTFT) perceived by the user.

### 2.5 Speculative Decoding Draft Loop (Optional / Advanced) (Leviathan et al., 2023)
To reduce Inter-Token Latency, a smaller "draft" model (e.g., Llama-3-8B) is loaded on the same or adjacent GPUs.
1. The draft model generates a sequence of 3-5 tokens rapidly.
2. These tokens are appended to the input of the 70B target model.
3. The 70B model performs a single forward pass, scoring the drafted tokens.
4. Accepted tokens are streamed to the client; rejected tokens trigger a correction, and the draft loop restarts.

## 3. Capacity & Performance Modeling (Worked Scenario)

*Note: The theoretical bounds presented below are derived strictly from hardware specifications and serve as analytical roofline limits, not measured guarantees of deployed systems.*

### 3.1 Model & Hardware Configuration
- **Model:** Llama-3-70B (Meta, 2024)
- **Configuration:** 80 layers, 64 attention heads (Q), 8 KV heads, head dimension of 128.
- **Data Type:** FP16 (2 bytes/value).
- **Context Length:** 4,096 tokens per request.
- **Hardware:** 8 × NVIDIA A100 SXM4 80GB GPUs (NVIDIA, 2020).
  - **Memory Capacity:** 80 GiB per GPU.
  - **Memory Bandwidth:** 2,039 GB/s per GPU.
- **Tensor Parallelism (TP):** TP=8 (1 KV head per GPU).

### 3.2 VRAM Budgeting (GB vs GiB)
We strictly separate the nominal VRAM into distinct pools to prevent over-allocation.
* Nominal Capacity: 8 × 80 GiB = **640.0 GiB** total.
* Weights (FP16): 70 billion parameters × 2 bytes = ~140 GB ≈ **130.4 GiB**.
* Workspace / Activations / Runtime Reserve: Assume 8 GiB per GPU = **64.0 GiB** total.
* **Nominal KV Cache Pool:** 640.0 - 130.4 - 64.0 = **445.6 GiB**.
* Allocator Fragmentation & Overhead: Assume 5% of KV pool = **22.3 GiB**.
* **Usable KV Cache Pool:** 445.6 - 22.3 = **423.3 GiB**.

### 3.3 Concurrency & Throughput
Using the explicit formula for KV cache size:
`KV = 2 × layers × KV heads × head dimension × token count × batch × bytes/value`

For a single request (batch = 1) at a context length of 4,096 tokens:
`KV per request = 2 × 80 × 8 × 128 × 4096 × 1 × 2 = 1,342,177,280 bytes ≈ 1.25 GiB`

**Maximum Concurrency (Theoretical Bound):**
`Max Concurrent Requests = Usable KV Cache Pool / KV per request = 423.3 GiB / 1.25 GiB ≈ 338 requests`

### 3.4 Theoretical Roofline Bounds
The Decode Phase is memory-bandwidth bound. Generating one token requires loading the entire model weights (assuming batch size 1).
- **Theoretical Lower Bound for Inter-Token Latency (ITL):**
  - Data to read per GPU: 130.4 GiB / 8 = 16.3 GiB.
  - Bandwidth per GPU: 2,039 GB/s ≈ 1,898 GiB/s.
  - `Theoretical ITL (Batch=1) = 16.3 GiB / 1,898 GiB/s ≈ 8.59 ms`.
*Note: This 8.59 ms is a theoretical hardware limit based purely on memory bandwidth for reading weights, ignoring compute time, communication overhead, and KV cache reading.*

## 4. Request Lifecycle (The Execution Loop)

1.  **Ingest:** Client sends prompt. Gateway tokenizes and adds to `Waiting` queue.
2.  **Schedule (Pre-fill):** Scheduler allocates initial KV cache blocks. Worker executes pre-fill pass. First token generated and streamed.
3.  **Schedule (Decode):** Request enters `Running` queue. Scheduler iteratively allocates new blocks as needed. Worker executes decode pass, generating subsequent tokens.
4.  **Finish:** Stop token generated. Request evicted. KV cache blocks freed (or retained in RadixTree for prefix caching). Response finalized.

## 5. Error Handling and Resilience
-   **OOM Prevention:** If the KV cache grows unexpectedly and VRAM is exhausted, the scheduler preempts active requests, swapping their KV blocks to CPU RAM, allowing higher-priority requests to complete.
-   **Worker Failure:** If a GPU worker fails, the entire tensor parallel group is compromised. The node is marked unhealthy, and traffic is routed to healthy nodes.

## 6. Cost and Efficiency Considerations
-   **Batch Size:** Maximizing batch size is crucial for amortizing the memory bandwidth cost. PagedAttention is the key enabler for large batch sizes.
-   **Quantization:** Using FP8 or INT8 quantization for weights and/or KV cache significantly reduces memory footprint, allowing larger models to fit on fewer GPUs or enabling larger batch sizes.

## 7. API Contracts

```http
POST /v1/completions
Content-Type: application/json
Authorization: Bearer <token>

{
  "model": "llama-3-70b-instruct",
  "prompt": "Explain continuous batching...",
  "max_tokens": 512,
  "temperature": 0.7,
  "stream": true
}
```

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream

data: {"id": "cmpl-1", "choices": [{"text": "Con"}]}
data: {"id": "cmpl-1", "choices": [{"text": "tinuous"}]}
data: {"id": "cmpl-1", "choices": [{"text": " batching"}]}
...
```
