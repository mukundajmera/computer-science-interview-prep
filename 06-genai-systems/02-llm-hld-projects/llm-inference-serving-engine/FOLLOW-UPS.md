# 🔮 Follow-up Questions: LLM Inference Serving Engine

## 1. Handling Extreme Context Lengths
**Question:** How does the design change if we need to support a 1-million-token context window (e.g., Gemini 1.5 Pro)?
**Answer:** The KV cache for a single request becomes massive, potentially exceeding the VRAM of an 8-GPU node.
-   **Ring Attention / Context Parallelism:** Partition the sequence dimension across multiple GPUs, passing KV blocks in a ring topology.
-   **KV Cache Quantization:** Compress the KV cache from FP16 to FP8 or INT4 to fit more blocks into memory.
-   **Prompt Caching:** Aggressively cache the prefix tree to avoid recomputing the 1M token pre-fill.

## 2. LoRA / Multi-Tenant Serving
**Question:** We want to serve 1,000 different fine-tuned models (LoRAs) based on a single base model. How do you adapt the architecture?
**Answer:** Loading 1,000 distinct models is cost-prohibitive.
-   **Base Model + LoRA Adapters:** Load the large base model weights once into the worker pool.
-   **Dynamic LoRA Loading:** Store the small LoRA adapters in CPU RAM or fast SSDs.
-   **Heterogeneous Batching:** Modify the scheduler to batch requests targeting different LoRAs together. The worker applies the base model computations to all requests, and applies the specific LoRA adapter updates only to the relevant requests in the batch.

## 3. Chunked Pre-fill
**Question:** A request with a 10,000-token prompt arrives while 10 other requests are in the decode phase. The pre-fill takes 500ms, stalling the decode requests and spiking their Inter-Token Latency. How do you fix this?
**Answer:** Implement Chunked Pre-fill.
-   Split the 10,000-token prompt into chunks (e.g., 512 tokens each).
-   In a single iteration, the scheduler mixes decode tokens for the 10 active requests with one 512-token chunk of the new prompt.
-   This bounds the iteration time, keeping ITL low for active requests while progressively building the KV cache for the new request, at the expense of a slightly higher TTFT for the new request.

## 4. Hardware Failures
**Question:** One GPU in an 8-GPU tensor parallel node fails during generation. What happens?
**Answer:** Because tensor parallelism requires synchronous `AllReduce` operations across all GPUs for every layer, a single GPU failure halts the entire node.
-   **Detection:** The scheduler or orchestration layer (e.g., Kubernetes) detects the failure via heartbeat or CUDA errors.
-   **Evacuation:** Active requests on that node are marked as failed (and retried by the Gateway on a healthy node, unfortunately from scratch).
-   **Recovery:** The node is removed from the routing pool until repaired. State cannot be easily salvaged from a partially failed tensor parallel group.
