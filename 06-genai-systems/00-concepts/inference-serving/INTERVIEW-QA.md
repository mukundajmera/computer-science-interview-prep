# Interview Q&A: LLM Inference Serving

## 1. What is the difference between the Prefill and Decode phases in LLM inference?
**Answer:** 
The Prefill phase processes the entire input prompt simultaneously to compute the initial KV-Cache and generate the first token. It is compute-bound (highly parallelizable) and measured by Time To First Token (TTFT). 
The Decode phase generates subsequent tokens autoregressively, one by one. It is memory bandwidth-bound, as the entire model weights and KV-cache must be loaded from GPU memory for each token. It is measured by Time Per Output Token (TPOT).

## 2. Walk me through the KV-Cache memory math for a 70B parameter model.
**Answer:** 
The KV-cache memory per token is: `2 * Number of Layers * Number of KV Heads * Head Dimension * Bytes per parameter`. 
For Llama-2-70B (FP16):
- Layers = 80
- KV Heads = 8 (using GQA)
- Head Dimension = 128
- Bytes per param = 2
Per token: `2 * 80 * 8 * 128 * 2 = 327,680 bytes (~327 KB)`.
For a batch of 32 requests, each with 4,096 tokens context: `32 * 4096 * 327KB ≈ 42.9 GB` of VRAM just for the KV-cache, highlighting why memory management is critical.

## 3. How does Continuous Batching improve throughput compared to static batching?
**Answer:** 
Static batching waits for the longest request in a batch to finish before starting a new batch, wasting massive compute resources as shorter requests finish early. Continuous (in-flight) batching dynamically adds and removes requests at the token level. When a request completes, a new one is immediately slotted into the batch for the next token iteration, dramatically increasing GPU utilization.

## 4. What problem does PagedAttention solve, and how does it work?
**Answer:** 
PagedAttention solves KV-cache memory fragmentation. Traditionally, memory for a request's max sequence length was pre-allocated contiguously, leading to huge internal and external fragmentation (up to 60-80% waste). PagedAttention borrows from OS virtual memory, dividing KV-cache into fixed-size blocks (pages). Memory is allocated non-contiguously on demand, and a page table maps logical tokens to physical blocks, virtually eliminating external fragmentation and enabling much larger batch sizes.

## 5. What is Chunked Prefill and why is it necessary?
**Answer:** 
Mixing prefill (compute-bound) and decode (memory-bound) phases in continuous batching causes problems. A large prefill request (e.g., 4K tokens) will stall all ongoing decode requests, causing latency spikes. Chunked prefill breaks the large prompt into smaller chunks (e.g., 512 tokens) and interleaves processing these chunks with the decode steps of other requests. This smooths out TPOT and prevents latency spikes.

## 6. How does Prefix Caching work and when is it most beneficial?
**Answer:** 
Prefix caching (or prompt caching) stores the KV-cache of shared input sequences (like a common system prompt or long document). When a new request arrives with a matching prefix, the engine reuses the cached KV blocks instead of recomputing them. It is highly beneficial when many users share the same system prompt, reducing TTFT drastically and saving compute costs.

## 7. Explain Speculative Decoding and provide a speedup calculation.
**Answer:** 
Speculative decoding uses a small, fast draft model to generate a sequence of $K$ tokens. The large target model then verifies these tokens in a single forward pass.
**Math:** 
Let target step = 20ms, draft step = 2ms, $K=4$ draft tokens, and average accepted tokens $\gamma = 2.5$.
Standard generation (1 token) = 20ms.
Speculative generation (verifying $K$ tokens) = $4 * 2ms + 20ms = 28ms$.
Speedup = $(\gamma * 20ms) / 28ms = (2.5 * 20) / 28 pprox 1.78x$ speedup.

## 8. What are the trade-offs of using Quantization in serving?
**Answer:** 
Quantization reduces weight precision (e.g., FP16 to INT8 or INT4).
- **Pros:** Massively reduces memory footprint, allowing larger models to fit on fewer GPUs. It also increases generation speed (reduces TPOT) because less data needs to be transferred from memory to compute cores.
- **Cons:** It can cause a slight degradation in model quality/accuracy, especially on complex reasoning tasks or at very low precision (INT4).

## 9. Contrast Tensor Parallelism (TP) with Pipeline Parallelism (PP).
**Answer:** 
- **Tensor Parallelism (TP):** Splits individual matrix operations across GPUs. It reduces latency (TPOT) and requires very high bandwidth (NVLink), restricting it to a single node.
- **Pipeline Parallelism (PP):** Splits the model layer-by-layer across GPUs. It allows scaling beyond a single node for massive models but does not reduce TPOT and introduces idle "bubble" time.

## 10. What is Disaggregated Serving?
**Answer:** 
Disaggregated serving separates the prefill and decode phases onto entirely different hardware pools. Prefill workers are optimized for compute to process long prompts quickly. Decode workers are optimized for memory bandwidth to generate tokens. The KV-cache generated by the prefill worker is transferred over a high-speed network (like RDMA) to the decode worker. This prevents resource contention and improves overall cluster utilization.

## 11. How does Multi-LoRA serving work in systems like vLLM or LoRAX?
**Answer:** 
Instead of loading multiple full copies of fine-tuned models, Multi-LoRA serving loads a single base model into GPU memory. Thousands of small LoRA adapters (~100MB each) are stored in CPU RAM. As requests arrive, the specific adapter needed is dynamically swapped into GPU memory and applied on top of the base model weights during the forward pass, allowing highly cost-effective multi-tenant serving.

## 12. Why is autoscaling LLM inference difficult?
**Answer:** 
Traditional metrics like CPU/Memory usage don't map well to LLM workloads. LLMs are constrained by KV-cache capacity and GPU memory bandwidth. Scaling up takes time because loading massive model weights into VRAM is slow (minutes). Therefore, scaling must be based on metrics like KV-cache utilization, queue length, or active requests per GPU, and often requires maintaining warm pools to mitigate cold starts.

## 13. What are the key SLOs (Service Level Objectives) for an LLM API?
**Answer:** 
1. **TTFT (Time To First Token):** Critical for perceived responsiveness in chat applications (target < 1-2s).
2. **TPOT (Time Per Output Token):** Determines the generation speed (target < 50ms/token to outpace reading speed).
3. **Throughput:** Total tokens generated per second per GPU, essential for measuring system cost-efficiency.

## 14. Compare vLLM, TGI, and TensorRT-LLM.
**Answer:** 
- **vLLM:** The pioneer of PagedAttention, highly flexible, great for general high-throughput production serving.
- **TGI (Text Generation Inference):** Built by Hugging Face (Rust backend), integrates tightly with the HF ecosystem, includes many production guardrails.
- **TensorRT-LLM:** Nvidia's proprietary engine. Highly optimized kernels for specific Nvidia architectures, offering maximum theoretical performance but with a steeper learning curve and compilation steps.

## 15. Why is the cost per 1M output tokens generally higher than input tokens?
**Answer:** 
Input tokens are processed during the prefill phase, which utilizes highly parallel matrix multiplications (compute-bound) and is very efficient. Output tokens are generated during the autoregressive decode phase, which requires loading the entire model weights for every single token (memory-bound). This inefficiency makes generating output tokens significantly more computationally expensive and time-consuming.

## 16. What happens if a model runs out of KV-Cache space?
**Answer:** 
In traditional systems, it results in an Out Of Memory (OOM) error, crashing the process. In modern systems utilizing PagedAttention (like vLLM), the engine will typically pause the generation, swap the request's KV-cache to CPU memory (preemption), and recompute or swap it back in when GPU memory becomes available, avoiding a crash but causing a massive latency spike.

## 17. How does Expert Parallelism (EP) work in MoE models?
**Answer:** 
In Mixture-of-Experts models, Expert Parallelism distributes different "experts" across different GPUs. During inference, the routing network determines which experts are needed for a specific token, and the token is sent to the corresponding GPU. This allows scaling model capacity massively without increasing the compute required per token.

## 18. What is the main failure mode of Speculative Decoding?
**Answer:** 
If the draft model's predictions frequently diverge from the target model's distribution (low acceptance rate $\gamma$), the large model will reject most draft tokens. The system then incurs the overhead of running the draft model *and* the target model without generating multiple tokens, resulting in slower inference than standard decoding.

## 19. How do you decide between Prompt Caching and Semantic Caching?
**Answer:** 
- **Prompt Caching (Prefix Caching):** Stores KV-cache of exact prompt prefixes. Use this when many users share the identical system prompt. It guarantees exact model outputs.
- **Semantic Caching:** Stores embeddings of questions and final text answers in a vector DB. If a similar question is asked, it returns the cached text without calling the LLM. Use this for FAQ-style traffic where slight variations in answers are acceptable, as it completely bypasses inference costs.

## 20. In what scenario would you choose Tensor Parallelism over Pipeline Parallelism?
**Answer:** 
You choose Tensor Parallelism when you need to minimize latency (TPOT) and your model fits within the GPUs of a single physical node (e.g., 8x H100s connected by NVLink). You choose Pipeline Parallelism when serving a massive model that requires more GPUs than exist in a single node, prioritizing capacity over single-request latency.

## 21. How do you mitigate 'head-of-line blocking' in an inference server?
**Answer:**
Head-of-line blocking occurs when a request generating a massive response (e.g., 4000 tokens) consumes GPU resources and prevents shorter requests from completing. It is mitigated by using continuous batching, which interleaves the execution of all active requests. Additionally, implementing advanced scheduling policies like Shortest Request First (SRF) or token-level fair-share algorithms ensures that long-running tasks don't starve newly arriving, smaller tasks.

## 22. What is the impact of Beam Search on KV-Cache memory during serving?
**Answer:**
Beam search explores multiple generation paths (beams) simultaneously to optimize output quality. If the beam width is $B$ (e.g., $B=4$), the inference engine must maintain $B$ distinct, active KV-cache sequences for a single user request. This quadruples the memory requirement compared to greedy decoding or sampling, drastically reducing the total number of concurrent users the server can handle, which is why it is rarely used in real-time APIs.

## 23. Explain how Finite State Machines (FSMs) are used in structured output generation.
**Answer:**
When an API requires strict JSON output, the engine must constrain the LLM's token generation. Instead of just relying on prompt engineering, engines can compile the required JSON schema into a Finite State Machine or regex parser. During the decode phase, this FSM integrates directly with the attention kernel, forcing the probability of any token that violates the schema to zero. This guarantees 100% valid output but adds computational overhead to the Time Per Output Token (TPOT).

## 24. What is the difference between TTFT and TTFB in the context of LLM APIs?
**Answer:**
- **Time To First Token (TTFT):** An internal metric measuring the time the GPU takes to process the prefill phase and generate the very first output token.
- **Time To First Byte (TTFB):** An external, user-facing metric measuring the time from when the user clicks 'send' to when the first byte of data is received by their browser. It includes TTFT plus all network latency, API gateway routing, and internet transit time.

## 25. Why are Server-Sent Events (SSE) preferred over standard REST polling for LLMs?
**Answer:**
LLM generation is slow and autoregressive. Waiting for a 1000-token response to finish before sending a single HTTP payload would result in a massive, unacceptable delay for the user. SSE allows the server to push tokens to the client over a single HTTP connection the moment they are generated by the GPU, providing a smooth streaming experience without the overhead of WebSockets or the inefficiency of continuous REST polling.

## 26. In multi-tenant serving, how do you prevent a single tenant from exhausting the KV-cache?
**Answer:**
A malicious or high-volume tenant could flood the server with long-context requests, consuming all available KV-cache blocks and causing OOM preemption for everyone else. This is prevented by implementing Fair Share Scheduling at the API gateway or inference engine level. The system tracks active tokens/blocks per tenant and enforces quotas; requests from tenants exceeding their quota are queued or their active KV-caches are preempted (swapped to CPU) in favor of tenants operating under their quota.

## 27. How does Kubernetes manage the deployment of large LLMs given slow startup times?
**Answer:**
Loading a 140GB model from network storage into GPU VRAM can take several minutes. If Kubernetes instantly routes traffic to a newly created pod, those requests will time out. This is managed by configuring strict Readiness Probes. The pod is not marked as "Ready" in the Kubernetes service mesh until the inference engine verifies that the weights are fully loaded and the KV-cache memory pool is initialized, ensuring traffic only hits warmed-up instances.

## 28. What dictates the choice between Swapping and Recomputation when preempting a request?
**Answer:**
When VRAM is full and a request must be paused, the engine can swap the KV-cache to CPU RAM or delete it (recomputation).
- **Swapping:** Used when PCIe bandwidth is available; it's faster to resume but consumes system RAM.
- **Recomputation:** Used if swapping is too slow or CPU RAM is full. To resume, the engine must run the compute-heavy prefill phase again. The scheduler dynamically chooses based on current hardware utilization and the length of the sequence (recomputing 100 tokens is cheap; recomputing 8000 tokens is expensive).

## 29. How does Model Sparsity (like Mixture-of-Experts) change inference memory constraints?
**Answer:**
In a dense model (like Llama-3-70B), all 70B parameters are loaded and active for every token. In a sparse MoE model (like Mixtral 8x7B), the total parameter count is large (~47B), meaning the *weight memory* requirement is still high. However, only a subset of experts (e.g., ~13B parameters) are activated for any given token. This means the *compute* required during decode is much lower, allowing for higher theoretical throughput if memory bandwidth bottlenecks can be overcome.

## 30. Why is standard CPU/Memory autoscaling dangerous for LLM inference pods?
**Answer:**
Standard autoscalers (like HPA in Kubernetes) scale up when CPU hits 80%. However, an LLM serving pod might be completely out of GPU VRAM (KV-cache is full) and dropping requests, while the host CPU sits at only 10% utilization. If scaling relies on CPU, the cluster will never scale up during an LLM overload. Autoscaling must be driven by custom metrics exposed by the engine, such as KV-cache block utilization or the length of the pending request queue.

## 31. Describe the impact of prompt length on TTFT.
**Answer:**
The Prefill phase (which dictates TTFT) processes the entire prompt in parallel using matrix multiplications. While it is compute-bound, the compute requirement scales quadratically with prompt length due to standard attention mechanisms (unless linear attention or FlashAttention is used). Therefore, a 100-token prompt might have a TTFT of 200ms, but a 10,000-token prompt might take several seconds to prefill, severely degrading perceived responsiveness.

## 32. What is the difference between Logit Biasing and FSM-guided generation?
**Answer:**
- **Logit Biasing:** A soft constraint. The engine adds a numerical bias to specific tokens (e.g., forbidding profanity) before the softmax step. It influences probability but doesn't guarantee structure.
- **FSM-guided:** A hard constraint. A Finite State Machine defines exact allowable token sequences (like strict JSON). If a token violates the state machine, its probability is set to negative infinity, guaranteeing the output strictly adheres to the schema.

## 33. How does Ring Attention solve the memory limitations of massive contexts?
**Answer:**
For models supporting 1M+ tokens, the KV-cache for a single sequence cannot fit on one GPU, causing an OOM. Ring Attention solves this by distributing the single long sequence across a "ring" of multiple GPUs. Each GPU holds a chunk of the KV-cache and computes local attention, passing the intermediate results around the ring. This allows scaling context length linearly with the number of GPUs.

## 34. What are the trade-offs of using an API Gateway to handle Semantic Caching?
**Answer:**
- **Pros:** It offloads work from the expensive GPU inference cluster. If a semantic match is found in the vector database, the gateway returns the cached response instantly, reducing latency to milliseconds and costing zero GPU cycles.
- **Cons:** It adds architectural complexity. Furthermore, setting the similarity threshold is difficult: too high, and the cache never hits; too low, and users receive slightly incorrect or stale answers, leading to hallucinations caused by the caching layer rather than the LLM.

## 35. Explain the concept of 'KV-Cache Offloading'.
**Answer:**
Unlike swapping (which happens dynamically when VRAM is full to prevent crashes), offloading (e.g., using frameworks like FlexGen) is a deliberate strategy to serve models larger than the available VRAM. Parts of the KV-cache (and sometimes weights) are intentionally kept on CPU RAM or even NVMe SSDs, and are streamed into the GPU only when needed. This allows massive batch sizes on weak hardware but at the cost of extremely high TPOT (slow generation).

## 36. Why is graceful shutdown critical for inference servers?
**Answer:**
When an orchestrator (like Kubernetes) scales down a cluster, it sends a termination signal to a pod. If the pod shuts down immediately, the active KV-caches stored in its VRAM are destroyed. Any user currently streaming a response will see their generation abruptly cut off mid-sentence. Graceful shutdown requires the engine to stop accepting new requests but remain alive until all currently generating requests finish and drain.

## 37. How does the choice of Tokenizer impact serving costs?
**Answer:**
LLMs process tokens, not words. If a tokenizer is inefficient for a specific language (e.g., it requires 3 tokens to represent a single Korean character, but only 1 token for an English word), serving that language will be much more expensive and slower. Since API providers charge per token and generation speed (TPOT) is measured in tokens, an inefficient tokenizer directly inflates the financial cost and latency for the end user.

## 38. What is the role of a 'Warm Pool' in LLM deployment architectures?
**Answer:**
Because LLMs take minutes to load from storage into VRAM (Cold Start), auto-scaling dynamically to handle sudden traffic spikes is too slow. A 'Warm Pool' is a set of active GPU instances with the model weights already loaded, sitting idle or handling background tasks. When traffic spikes, these instances instantly take on live traffic, ensuring TTFT SLOs are met without waiting for heavy model loads.

## 39. Compare the focus of vLLM versus TensorRT-LLM.
**Answer:**
- **vLLM:** Focused on ease of use, flexibility, and high-throughput production serving. It pioneered PagedAttention and is highly adaptable to various models and hardware via PyTorch.
- **TensorRT-LLM:** Nvidia's proprietary engine focused on absolute maximum performance. It requires compiling the model into an optimized TensorRT engine specifically for the target Nvidia architecture, offering lower latency but with a much steeper learning curve and hardware lock-in.

## 40. Why do output tokens cost more than input tokens on commercial APIs?
**Answer:**
Processing input tokens (prefill) relies on massive parallel matrix multiplications across the entire prompt sequence simultaneously; it is highly efficient and compute-bound. Generating output tokens (decode) is sequential; the GPU must load the entire model weights and KV-cache from VRAM for *every single token generated*. This memory-bound inefficiency means output generation utilizes the hardware poorly compared to prefill, driving up the actual compute cost.

## 41. How does hardware failure impact Disaggregated Serving architectures?
**Answer:**
In Disaggregated Serving, prefill and decode are handled by separate workers over a network. If a prefill worker fails during computation, only the prompt processing is lost; the client can retry. However, if a decode worker fails mid-generation, the entire KV-cache transferred to it is lost. The system must implement robust retry logic, routing the request to a new prefill worker to regenerate the KV-cache from scratch before sending it to a healthy decode worker, increasing latency recovery time.

## 42. Explain the concept of 'Context Window' limitations in hardware terms.
**Answer:**
The context window (e.g., 128k tokens) is not just a theoretical model limit; it represents a hard memory ceiling. Every token requires KV-cache storage. As the context approaches the maximum, the KV-cache consumes massive amounts of VRAM. If a model supports a 128k window, serving a single request at max context might require multiple GPUs just to hold the KV-cache, completely bypassing the single GPU's VRAM limits even if the model weights fit easily.

## 43. What is 'Weight Streaming' and when is it used?
**Answer:**
Weight streaming is an optimization for cold starts or edge deployments. Instead of waiting for a 140GB model to download completely before starting inference, the engine streams the weights layer-by-layer over the network. As soon as the first layers arrive, the prefill phase begins computing activations, overlapping the network download with GPU computation to drastically reduce perceived startup latency.

## 44. How does Intrinsic Dimensionality relate to LoRA serving?
**Answer:**
Intrinsic dimensionality suggests that large models can learn complex tasks by optimizing in a much smaller, lower-dimensional space. LoRA leverages this by injecting small, trainable low-rank matrices into the model. For serving, this means we only need to store these tiny matrices (megabytes) instead of full model copies (gigabytes). This mathematical property is what makes Multi-LoRA serving physically possible on a single GPU.

## 45. What is the difference between Token-by-Token streaming and Chunked streaming?
**Answer:**
- **Token-by-Token:** The server pushes every single token over SSE the millisecond it is generated. This provides the fastest perceived TTFB but causes high network overhead due to thousands of tiny HTTP frames.
- **Chunked Streaming:** The server buffers tokens (e.g., waits for 5 tokens or a complete word) before sending a chunk. This slightly increases TTFB but drastically reduces network packet overhead and CPU load on the API Gateway.

## 46. Describe the role of a 'Router Model' in inference pipelines.
**Answer:**
To balance cost and quality, a fast, cheap router model (or classifier) analyzes incoming prompts. Simple queries (e.g., "What is 2+2?") are routed to a small, cheap model (like Llama-8B) for fast inference. Complex reasoning queries are routed to a massive model (like GPT-4-class). This orchestration happens before the main prefill phase, optimizing the overall inference cluster utilization.

## 47. Why are 'System Prompts' ideal candidates for Prefix Caching?
**Answer:**
System prompts dictate the behavior of the AI (e.g., "You are a helpful assistant. Follow these strict rules..."). In production, thousands of users hit the API with different queries, but they all share the exact same system prompt prepended to their request. Because the text is identical and static, its KV-cache can be computed once, stored permanently via Prefix Caching, and reused instantly for every single user, bypassing the prefill compute cost entirely for that section.

## 48. How do 'Guardrails' impact inference latency?
**Answer:**
Guardrails (like toxicity filters or PII scrubbers) are often implemented as secondary ML models or regex engines.
- **Input Guardrails:** Run before prefill, adding latency to TTFT.
- **Output Guardrails:** Run on the generated text. If applied post-generation, they block streaming, forcing the user to wait for the entire response. If applied dynamically during streaming, they require buffering tokens before release, increasing perceived TPOT.

## 49. What is 'Continuous Batching' and why did it replace static batching?
**Answer:**
Static batching waits for a fixed group of requests to finish completely before taking new ones. If one request generates 1000 tokens and others generate 10, the GPU sits mostly idle for 990 steps. Continuous batching dynamically slots new requests into the active batch the exact moment a shorter request finishes. This token-level scheduling ensures the GPU is always fully utilized, multiplying throughput compared to static batching.

## 50. Explain the 'Memory Wall' in the context of LLM Decode.
**Answer:**
The 'Memory Wall' refers to the widening gap between processor speeds (FLOPs) and memory access speeds (Bandwidth). During the decode phase, the GPU must read the entire model weights (e.g., 140GB) from HBM to SRAM for every single token generated. Modern GPUs can compute matrix multiplications much faster than they can fetch this data. Therefore, the decode speed is entirely bottlenecked by how fast memory can be read, hitting the 'Memory Wall'.

## 51. What is the impact of Quantization on the Memory Wall?
**Answer:**
Quantization directly attacks the Memory Wall. By converting model weights from 16-bit (FP16) to 4-bit (INT4), the total size of the weights is reduced by 75%. During the decode phase, the GPU now only has to fetch 1/4th the amount of data from memory for every token. This drastically reduces the time spent waiting on memory bandwidth, resulting in significantly faster generation speeds (lower TPOT).

## 52. How does Speculative Decoding utilize the Memory Wall to gain speed?
**Answer:**
The large target model is bottlenecked by reading weights from memory, not by compute. Reading weights for 1 token takes nearly the same time as reading weights for 5 tokens if processed in parallel. Speculative decoding uses a tiny draft model to guess 5 tokens quickly. The large model then reads its weights *once* and verifies all 5 drafted tokens in parallel. By batching the verification, it bypasses the sequential memory read bottleneck.

## 53. What is the role of a 'Load Balancer' in LLM clusters?
**Answer:**
A standard round-robin load balancer is inefficient for LLMs because request compute costs vary wildly. LLM load balancers must be 'state-aware'. They route requests based on the current KV-cache utilization of specific workers, the presence of specific LoRA adapters already loaded in VRAM, or prefix cache hits (routing identical prompts to the same worker to maximize cache reuse).

## 54. Describe the failure mode: 'KV-Cache Fragmentation'.
**Answer:**
Before PagedAttention, KV-cache memory for a request was pre-allocated as a single contiguous block based on the maximum possible context length (e.g., 4096 tokens). If the request only generated 100 tokens, the remaining memory was wasted (internal fragmentation). Additionally, leaving varying-sized holes in memory prevented new requests from being scheduled (external fragmentation). This wasted up to 80% of VRAM, severely limiting concurrency.

## 55. How do you handle 'Aborted Requests' in an inference engine?
**Answer:**
If a user closes their browser or clicks "Stop Generation," the API Gateway drops the connection. The inference engine must detect this instantly. If it doesn't, the GPU will continue generating tokens, wasting expensive compute and blocking other users. The engine must immediately halt the generation loop for that request, free the associated physical blocks via PagedAttention, and decrement the reference counts for any shared prefix caches.

## 56. What is 'Batched Offline Inference' and how does it differ from online serving?
**Answer:**
Online serving (APIs) prioritizes TTFT and TPOT to provide a smooth streaming experience for human users. Batched offline inference (e.g., generating 10 million summaries overnight) does not care about latency; it only cares about total throughput (tokens/second/dollar). Offline engines use massive batch sizes, turn off streaming, and utilize techniques like DeepSpeed to maximize hardware utilization, ignoring strict latency SLOs entirely.

## 57. Explain the concept of 'Context Parallelism'.
**Answer:**
When context lengths reach massive sizes (e.g., 1 million tokens), the prefill matrix multiplications become too large for a single GPU. Context Parallelism splits a *single* input sequence across multiple GPUs. Each GPU computes the attention for its segment of the context. This requires complex communication patterns (like Ring Attention) to share Key/Value states across GPUs, enabling inference on infinitely long documents.

## 58. How do 'Early Exit' models optimize inference latency?
**Answer:**
Early Exit models add classifiers at intermediate transformer layers. During generation, if the model is highly confident about the next token at layer 12, it "exits" early and outputs the token without passing through the remaining 20 layers. This dynamic depth reduction saves massive amounts of compute and memory reads for simple tokens, significantly accelerating TPOT on average.

## 59. What are the security risks of allowing users to define their own 'Stop Sequences'?
**Answer:**
Stop sequences tell the engine to halt generation when a specific string is produced. If a user provides an extremely long or complex regex as a stop sequence, the engine must evaluate this against the output stream at every single token step. A maliciously crafted stop sequence could cause catastrophic backtracking or CPU exhaustion on the API Gateway or inference engine, acting as a Denial of Service (DoS) attack.

## 60. Why is 'Memory Bandwidth' often more critical than 'TFLOPs' when choosing GPUs for LLMs?
**Answer:**
While TFLOPs (compute power) dictate how fast the prefill phase runs, human-facing applications are dominated by the decode phase (generating the response). Decode is almost entirely constrained by how fast the weights can be read from VRAM (Memory Bandwidth). An architecture with massive compute but slow memory will sit idle during decode. Therefore, GPUs like the H100, which have incredibly high memory bandwidth, are the premium choice for LLM serving.

## 61. How does the 'Head Dimension' affect the KV-Cache memory footprint?
**Answer:**
The Head Dimension ($D$) is the size of the vector representation for each attention head. In the memory equation (`Bytes per token = 2 * L * H * D * bytes`), $D$ acts as a linear multiplier. While reducing $D$ would shrink the cache footprint, it reduces the model's expressivity and quality. Therefore, architectural innovations like Grouped Query Attention focus on reducing $H$ (number of KV heads) rather than $D$ to save memory while preserving quality.

## 62. What is the role of an 'Orchestrator' in a multi-model GenAI application?
**Answer:**
An application rarely uses just one model. An Orchestrator (like LangChain or custom middleware) sits above the inference engine. It routes requests: simple tasks go to small, cheap models; reasoning tasks go to large models; vector searches go to embedding models. It also handles fallback logic (if model A times out, call model B) and aggregates results, shielding the end-user from the complexity of the underlying serving infrastructure.

## 63. How do you load test an LLM inference server?
**Answer:**
Traditional HTTP load testing (like `ab` or `wrk`) is insufficient because it doesn't account for token generation lengths or KV-cache states. You must use specialized frameworks like Locust or custom scripts that simulate realistic LLM traffic patterns: varying prompt lengths, varying expected output lengths, and simulating streaming connections. The test must monitor TTFT, TPOT, and track when the server begins preempting requests due to KV-cache exhaustion.

## 64. Describe the 'Draft Model Selection' problem in Speculative Decoding.
**Answer:**
The success of Speculative Decoding hinges entirely on the draft model. It must be small enough to be extremely fast, but capable enough to guess the exact tokens the target model would produce. If the target is Llama-3-70B, a 7B model might be too slow to provide a speedup, while a 100M model might be too stupid, resulting in a 0% acceptance rate. Training specialized, distillation-based draft models specifically aligned to the target model is an active area of research.

## 65. What is the financial tradeoff between self-hosting and using Managed APIs?
**Answer:**
- **Self-Hosting (e.g., vLLM on AWS):** High fixed costs (renting GPUs monthly). Highly cost-effective at massive scale because the cost per token drops towards zero if GPUs run near 100% utilization. Gives total control over data privacy and custom models.
- **Managed APIs (e.g., OpenAI, Anthropic):** Pure variable cost (pay per token). Cheaper for low or bursty traffic because you don't pay for idle GPUs. No operational overhead, but you sacrifice privacy and custom LoRA capabilities.

## 66. Explain the concept of 'Token Healing'.
**Answer:**
Tokenization is often irreversible at the boundaries. If a user's prompt ends with a partial word, standard generation might produce a sub-optimal continuation because the tokenizer split the text awkwardly. Token Healing (implemented in engines like Guidance) intercepts the generation, looks at the raw text, and "heals" the boundary by forcing the model to complete the partial word logically before continuing with standard autoregressive generation, improving output quality.

## 67. How do 'Mixture of Depths' (MoD) models optimize serving?
**Answer:**
Similar to Early Exit, MoD dynamically routes tokens through the network. However, instead of exiting early, an MoD model learns to skip certain layers entirely for simple tokens. A token might only be processed by layers 1, 5, and 12. This reduces the total compute FLOPs required during both prefill and decode, accelerating TTFT and TPOT, while maintaining the capacity of a deep network for complex tokens.

## 68. What is the impact of 'System Prompt Drift' on Prefix Caching?
**Answer:**
If developers constantly tweak or A/B test the system prompt (e.g., changing a single word), they break the exact string match required for Prefix Caching. The inference engine must recompute the prefill phase for every minor variation, destroying the performance benefits. To leverage caching effectively, system prompts should be versioned and kept static for large cohorts of users.
