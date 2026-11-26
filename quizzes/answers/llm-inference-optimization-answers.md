# LLM Inference Optimization Quiz - Answer Key

## Answers

1. **A** - The KV (Key-Value) Cache, which stores the key and value tensors for all previous tokens to avoid recomputing them

**Explanation:**
During the decoding phase, the model generates one token at a time. To avoid recalculating the self-attention scores for all previous tokens at every step, the Key and Value tensors for past tokens are cached in GPU memory. This 'KV Cache' grows linearly with the sequence length and batch size, often exceeding the memory required for the model weights themselves in long-context or high-batch scenarios.

**Why other options fail:**
- **B**: While model weights are large, they are loaded into VRAM once and remain resident; they are not constantly swapped during generation.
- **C**: FFN activations only represent the memory for the single token currently being processed, which is negligible compared to the full context history.
- **D**: The embedding lookup is an O(1) operation per token that uses a fixed amount of memory independent of the context length.

---

2. **A** - It breaks the KV Cache into fixed-size blocks (pages) that are allocated non-contiguously, similar to virtual memory in operating systems

**Explanation:**
Standard KV Cache allocation requires contiguous blocks of memory for the maximum possible sequence length, leading to severe internal and external fragmentation (often >50% wasted space). PagedAttention, introduced in vLLM, solves this by partitioning the KV cache into fixed-size blocks (e.g., 16 tokens) that can be stored non-contiguously in memory, allowing for near-zero waste and enabling dynamic batching.

**Why other options fail:**
- **B**: Quantization reduces total memory footprint but does not solve the structural problem of contiguous allocation and fragmentation.
- **C**: Offloading handles capacity limits but is a separate technique (like DeepSpeed ZeRO); it does not solve fragmentation within VRAM.
- **D**: Attention heads are structurally fixed during training and cannot be dynamically resized during inference.

---

3. **D** - Injecting new requests into the batch as soon as a previous request finishes its generation, rather than waiting for the entire batch to complete

**Explanation:**
Traditional static batching waits for all sequences in a batch to finish generating before starting a new batch. Because sequence lengths vary wildly, GPUs sit idle waiting for the longest sequence. Continuous batching dynamically evicts finished requests and injects new requests at the iteration level (token-by-token), keeping GPU utilization high and drastically improving throughput.

**Why other options fail:**
- **A**: This is a description of an infinite loop bug, not an inference optimization technique.
- **B**: This describes split-phase execution, but continuous batching specifically refers to the dynamic joining and leaving of requests during decoding.
- **C**: Streaming weights from disk is related to offloading or unified memory, not batching strategies.

---

4. **C** - It reduces the latency (Time Per Output Token) of autoregressive generation by using a smaller, faster model to draft multiple tokens which the large model verifies in parallel

**Explanation:**
Autoregressive generation is memory-bandwidth bound (reading the huge model weights from HBM to compute cores for every token). Speculative Decoding uses a tiny 'draft' model to quickly generate a sequence of tokens. The large 'target' model then evaluates these drafted tokens in a single forward pass (which is parallelizable and compute-bound). If the target model agrees, multiple tokens are accepted in the time it usually takes to generate one, significantly reducing latency.

**Why other options fail:**
- **A**: KV Cache eviction is handled by techniques like Heavy Hitter Oracle (H2O) or StreamingLLM, not speculative decoding.
- **B**: Presenting multiple options is beam search or diverse decoding, not speculative decoding.
- **D**: The prefill phase processes actual user input; it cannot be bypassed by predicting the prompt before it arrives.

---

5. **A** - Splitting a very long input prompt into smaller chunks to prevent the prefill phase from causing long latency spikes for other requests concurrently generating tokens

**Explanation:**
The prefill phase (processing the prompt) is highly compute-intensive and can block the GPU for hundreds of milliseconds. If an LLM is serving multiple requests, a new request with a 10K-token prompt can stall the generation of tokens for all other users. Chunked prefill breaks the long prompt into smaller segments (e.g., 512 tokens), interleaving prefill computation with decoding steps for other requests, ensuring smooth continuous generation.

**Why other options fail:**
- **B**: Streaming output happens naturally token-by-token or word-by-word; it does not require 'chunked prefill'.
- **C**: Dividing weights across GPUs is Tensor Parallelism or Pipeline Parallelism.
- **D**: Chunking datasets is a data preparation step for training, unrelated to inference optimization.

---

6. **D** - It minimizes memory reads and writes by keeping the attention computation entirely within the fast on-chip SRAM, avoiding round-trips to the slower HBM

**Explanation:**
Standard attention implementations materialize an enormous NxN attention matrix in High Bandwidth Memory (HBM), which is heavily memory-bandwidth constrained. FlashAttention uses tiling to load blocks of Q, K, and V into the much faster on-chip SRAM, computes the attention (including softmax scaling) locally, and only writes the final output back to HBM. This dramatically reduces memory I/O, resulting in massive speedups.

**Why other options fail:**
- **A**: Disk I/O is orders of magnitude too slow for attention computations; FlashAttention optimizes on-chip memory.
- **B**: Skipping distant tokens describes sparse attention or sliding window attention (like Mistral), not FlashAttention.
- **C**: Linear approximations of Softmax exist (e.g., Performer), but FlashAttention computes exact standard Softmax.

---

7. **B** - The weights are kept in 4-bit in memory to save bandwidth, but are quickly dequantized to FP16 in the GPU registers just before the FP16 matrix multiplication occurs

**Explanation:**
During autoregressive decoding, the bottleneck is memory bandwidth (reading weights from HBM). Weight-only quantization stores the weights in 4-bit, cutting memory traffic by 4x compared to FP16. However, standard GPUs do not support native 4-bit matrix multiplication. Therefore, as the weights arrive in the compute cores (registers/SRAM), they are rapidly cast back to FP16, and the actual math is performed against the FP16 activations. The time saved reading from memory vastly outweighs the time spent dequantizing.

**Why other options fail:**
- **A**: Standard NVIDIA GPUs (pre-Blackwell) lack native INT4 tensor cores for direct matrix multiplication.
- **C**: Quantizing activations to 4-bit is notoriously difficult and usually causes severe accuracy degradation; this describes W4A4, which is extremely rare.
- **D**: CPUs are far too slow for LLM inference; quantization aims to keep the workload on the GPU while reducing memory bandwidth.

---

8. **A** - Splitting individual weight matrices (e.g., linear layers and attention heads) across multiple GPUs, so they collaboratively compute a single forward pass simultaneously

**Explanation:**
Tensor Parallelism slices the actual weight tensors. For example, in a multi-head attention layer, GPU 1 computes half the heads and GPU 2 computes the other half. They then communicate (via an All-Reduce operation over NVLink) to sum the results before moving to the next layer. This is required when a single model is too large to fit in one GPU's VRAM.

**Why other options fail:**
- **B**: Splitting sequence length describes Sequence Parallelism (like Ring Attention), which is distinct from Tensor Parallelism.
- **C**: Running identical copies is Data Parallelism or replica serving, not Tensor Parallelism.
- **D**: Splitting layers vertically is Pipeline Parallelism, where execution happens sequentially rather than simultaneously.

---

9. **B** - Time to First Token (TTFT) and Tokens Per Second (TPS)

**Explanation:**
In a streaming application (like ChatGPT), the user cares about two things: how fast the model starts typing (Time to First Token, governed by the prefill phase) and how fast it types the remaining words (Tokens Per Second or Time Per Output Token, governed by the decode phase). Total Generation Time is misleading because a 1000-token response will inherently take longer than a 10-token response, even if the TPS is excellent.

**Why other options fail:**
- **A**: Total Generation Time hides the speed at which words appear on the screen, which is what impacts user experience in streaming.
- **C**: Model loading time is a cold-start metric, but does not reflect per-request latency during active serving.
- **D**: Memory utilization is an infrastructure efficiency metric, not a user-facing latency metric.

---

10. **C** - The Prefill phase processes the entire input prompt in parallel (compute-bound), while the Decode phase generates output tokens sequentially one-by-one (memory-bandwidth bound)

**Explanation:**
During prefill, the entire input prompt (e.g., 1000 tokens) is known in advance. The model computes the self-attention and KV cache for all 1000 tokens simultaneously using highly efficient parallel matrix multiplications (compute-bound). During decode, each new token depends on the previous one, forcing the GPU to load the massive model weights repeatedly to compute just a single token at a time (memory-bandwidth bound).

**Why other options fail:**
- **A**: Prefill processes the input; it does not generate output tokens.
- **B**: Both phases run on the GPU; moving prefill to the CPU would introduce unacceptable PCIe transfer latency.
- **D**: Inference does not update model weights; weight updates only happen during training or fine-tuning.

---

11. **C** - Larger batches amortize the cost of loading model weights from memory across multiple requests, increasing throughput, but computing larger matrices eventually takes physical time in the Tensor Cores, slowing individual generation.

**Explanation:**
During decoding, reading the weights from memory is the bottleneck. If you batch 16 requests, you read the weights once and use them for 16 tokens simultaneously. This vastly increases total throughput. However, as batch size grows very large (e.g., 256), the actual matrix multiplications become large enough that the compute cores become saturated. At that point, the system transitions from memory-bound to compute-bound, and individual requests (measured by Time Per Output Token, TPOT) take a bit longer.

**Why other options fail:**
- **A**: Batching relies heavily on the KV Cache; bypassing it would make TPOT catastrophically slow as context is recomputed.
- **B**: Batch size does not affect the number of tokens generated per request; that is determined by the prompt and stopping criteria.
- **D**: Batching and Speculative Decoding are largely orthogonal; in fact, Speculative Decoding is often harder to implement efficiently at high batch sizes.

---

12. **B** - Reusing the KV cache for common prompt prefixes (like system prompts or large context documents) across different user requests

**Explanation:**
Many requests share identical system prompts or large context blocks (e.g., 'You are a helpful assistant...' or a large PDF in a multi-turn chat). Prefix caching stores the computed KV cache for these shared prefixes. When a new request arrives with the same prefix, the system directly loads the KV cache instead of recomputing the prefill phase, saving massive compute and drastically reducing TTFT.

**Why other options fail:**
- **A**: Caching textual output is semantic caching, not prefix caching, and it only helps if the exact query is repeated.
- **C**: Vocabulary embeddings are already in VRAM; pre-computing them in CPU RAM would slow down inference due to PCIe bottlenecks.
- **D**: API gateway caching is a networking optimization, completely separate from LLM prompt processing.

---

13. **D** - Receiving a batch of requests where one request has an extremely long prompt and another generates an extremely long response, forcing memory allocation for the maximum possible grid

**Explanation:**
In naive static batching, memory is pre-allocated based on the maximum sequence length and maximum batch size. If you batch a 100-token input/1000-token output request with a 1000-token input/100-token output request, static batching allocates memory as if *both* requests will reach the absolute maximum size (e.g., 2000 tokens). This massive padding wastes VRAM and easily triggers OOM errors.

**Why other options fail:**
- **A**: Identical system prompts allow for prefix caching, which saves memory, rather than causing OOM.
- **B**: INT8 requires half the memory of FP16, heavily reducing the risk of OOM.
- **C**: Tensor Parallelism splits memory requirements across multiple GPUs, reducing the VRAM burden on any single device.

---

14. **A** - It swaps inactive or older blocks of the KV cache from the GPU VRAM to the host CPU RAM via PCIe, retrieving them only when needed

**Explanation:**
When generating very long context, the KV cache can exceed VRAM. Offloading systems (like DeepSpeed or FlexGen) dynamically move blocks of the KV cache to the much larger (but slower) CPU RAM via the PCIe bus. When the attention mechanism needs to attend to older tokens, those blocks are fetched back to the GPU. This sacrifices some speed for the ability to handle massive context lengths.

**Why other options fail:**
- **B**: Cloud storage (like S3) has latencies in tens or hundreds of milliseconds, which is catastrophic for token generation speeds.
- **C**: Deleting oldest blocks permanently is a technique like StreamingLLM, not offloading; it permanently loses that context.
- **D**: Gzip is a generic file compressor and cannot be computed fast enough by Tensor Cores for real-time memory compression.

---

15. **D** - Medusa adds multiple extra decoding heads to the LLM to predict several future tokens simultaneously in a single forward pass, without needing a separate draft model

**Explanation:**
Unlike standard Speculative Decoding which requires a separate 'draft' model, Medusa (and similar techniques) trains multiple extra output heads attached to the final layer of the *target* model. In one forward pass, Head 1 predicts token n+1, Head 2 predicts n+2, etc. These predictions are then verified against the actual causal graph, allowing multiple tokens to be accepted per step without managing two separate models.

**Why other options fail:**
- **A**: Tree-search for code is an application-level decoding strategy (like MCTS), not the core architectural change introduced by Medusa.
- **B**: Using a separate smaller model is standard Speculative Decoding, which Medusa explicitly avoids to reduce deployment complexity.
- **C**: Bidirectional attention is used in models like BERT; autoregressive generation strictly requires causal (unidirectional) masking.

---

16. **C** - The time it takes to read the entire model's weights from HBM to SRAM for every single generated token

**Explanation:**
During the decoding phase (batch size = 1 or small batch), the compute required is minimal (a vector-matrix multiplication). The GPU Tensor Cores sit idle waiting for data. The absolute bottleneck is memory bandwidth: the physical time it takes to transfer the multi-gigabyte model weights from High Bandwidth Memory (HBM) into the compute cores (SRAM) for *every single token* generated.

**Why other options fail:**
- **A**: Network latency impacts Time To First Token (TTFT) but does not bottleneck the GPU's internal Time Per Output Token (TPOT).
- **B**: Tensor Cores are incredibly fast and heavily underutilized during decoding; compute time is a fraction of memory read time.
- **D**: Embeddings are loaded into VRAM during initialization, not read from disk during generation.

---

17. **B** - It restricts the attention mechanism to only look back at the most recent N tokens, meaning the KV Cache never grows beyond N tokens in size

**Explanation:**
In standard attention, the KV cache grows indefinitely with the sequence length. Sliding Window Attention (SWA) limits the attention span to a fixed window (e.g., 4096 tokens). Token 5000 only attends to tokens 904 through 5000. Therefore, the KV cache only needs to hold 4096 tokens at any time; older tokens are evicted, keeping memory usage constant and bounded regardless of generation length.

**Why other options fail:**
- **A**: Model weights remain static on their assigned GPUs; sliding weights would ruin inference speed via interconnect overhead.
- **C**: Prompt character limits are handled by application logic (UI/API), not by the model's internal attention mechanism.
- **D**: Convolution filters are used in CNNs for vision tasks, not for managing KV cache memory in Transformers.

---

18. **D** - FP8 provides a better dynamic range for representing outliers in activations and weights without the complex scaling factors required by integer quantization

**Explanation:**
LLM activations often contain extreme outliers (very large values) that are critical to performance. Integer quantization (INT8) has a uniform distribution and struggles to represent these outliers without complex, fine-grained scaling algorithms. Floating Point 8 (FP8) maintains an exponent and a mantissa, providing a much wider dynamic range, naturally handling outliers and preserving accuracy with less engineering overhead.

**Why other options fail:**
- **A**: Both FP8 and INT8 use exactly 8 bits in memory; the difference lies in how those 8 bits are interpreted.
- **B**: Hallucinations are an alignment and training issue; hardware data formats dictate precision, not factual accuracy.
- **C**: CPUs traditionally lack FP8 support; it is heavily reliant on specialized accelerators like Nvidia Hopper architectures.

---

19. **B** - Splitting the model layer-by-layer across multiple GPUs (e.g., layers 1-4 on GPU1, 5-8 on GPU2), passing the hidden states sequentially between them

**Explanation:**
Pipeline Parallelism partitions the model sequentially. GPU 1 holds the first few layers, processes the data, and sends the hidden states (activations) over the network to GPU 2, which holds the next layers. While TP splits tensors for parallel math, PP splits layers for sequential processing. It requires careful micro-batching to avoid GPUs sitting idle (pipeline bubbles).

**Why other options fail:**
- **A**: Slicing individual weight matrices describes Tensor Parallelism, which happens within a layer rather than across layers.
- **C**: Running identical copies for load balancing describes Data Parallelism.
- **D**: Streaming training data is a data pipeline concern, not a model parallelism technique used for inference.

---

20. **C** - It distributes the context window (sequence length) across multiple GPUs in a ring topology, allowing the model to process sequences far larger than a single GPU's VRAM can hold

**Explanation:**
When processing millions of tokens (like a 1M token context window), the KV cache and attention computation are far too large for one GPU, even if weights are small. Ring Attention (a form of Sequence Parallelism) splits the sequence length across multiple GPUs connected in a ring. The GPUs pass blocks of Keys and Values in a circle, computing partial attention scores until the full sequence context is resolved.

**Why other options fail:**
- **A**: Restricting attention to nearest neighbors is local attention; Ring Attention computes exact global attention.
- **B**: A circular buffer that loops over itself is essentially sliding window attention, which inherently drops older context; Ring Attention retains full context.
- **D**: Generating tokens in an infinite loop is a failure mode, not a targeted architectural feature.

---


21. **B** - The MoE model requires the same total VRAM capacity to store the weights, but significantly reduces the active compute (FLOPs) and memory bandwidth required per generated token

**Explanation:**
A Sparse MoE model contains many 'expert' sub-networks, but a router only activates a small subset of them for any given token (e.g., 2 out of 8 experts). While the compute (FLOPs) and memory bandwidth required *per token* drop to match the size of the active parameters (enabling faster generation or larger batch sizes), the entire set of weights must still reside in VRAM to prevent unacceptable latency from swapping experts. Therefore, a 47B parameter MoE requires the VRAM of a 47B dense model, but runs with the speed of a ~13B dense model.

**Why other options fail:**
- **A**: Offloading inactive experts to CPU or disk during real-time autoregressive generation is too slow due to PCIe/interconnect bottlenecks; all experts must stay in VRAM.
- **C**: Compute (FLOPs) is drastically reduced because not all experts are evaluated for each token.
- **D**: KV cache fragmentation is an orthogonal memory management issue (solved by techniques like PagedAttention), unrelated to MoE architecture.


---

22. **B** - It parallelizes the attention computation across the sequence length dimension of the KV cache, allowing multiple thread blocks to process different chunks of the past context simultaneously, which is critical when batch sizes are small and contexts are long

**Explanation:**
During the decoding phase, standard FlashAttention parallelizes computation across batch size and number of heads. However, with small batch sizes (e.g., 1) and very long contexts, this leaves the GPU heavily underutilized. Flash-Decoding splits the KV cache along the sequence length, assigning different blocks of the sequence to different GPU thread blocks to compute partial attention scores in parallel. These partial results are then quickly reduced using a secondary operation, massively speeding up attention computation for long-context generation.

**Why other options fail:**
- **A**: While KV cache quantization (like INT8/FP8 KV cache) is a valid memory optimization, it is completely distinct from Flash-Decoding, which focuses on algorithmic parallelization across thread blocks.
- **C**: Flash-Decoding computes exact attention, not a sparse or linear approximation.
- **D**: Attention cannot be bypassed for recent tokens, as they are strictly required for accurate causal generation, and FFN activations do not replace the need for KV cross-attention.

23. **B** - It caches the KV cache in a radix tree structure, enabling efficient reuse of identical token prefixes across multiple requests to reduce prefill latency

**Explanation:**
RadixAttention optimizes memory and compute by structuring the KV cache as a radix tree (a type of prefix tree). This allows the inference engine to automatically detect and reuse the KV cache for shared prefixes (like identical system prompts, few-shot examples, or conversational history) across multiple, concurrent requests. By avoiding the recomputation of these shared prefixes during the prefill phase, RadixAttention significantly reduces Time To First Token (TTFT) and saves GPU memory.

**Why other options fail:**
- **A**: Quantizing the KV cache to lower precision (e.g., FP8 or INT8) is a different optimization technique, not RadixAttention.
- **C**: RadixAttention computes exact attention, not a sparse or linear approximation.
- **D**: Parallelizing attention across the sequence length dimension is a feature of Flash-Decoding, not RadixAttention.


24. **B** - To receive tokens from the Worker Pool, detokenize them, and immediately stream Server-Sent Events (SSE) back to the client to minimize Time To First Token (TTFT)

**Explanation:**
As the Worker Pool completes iterations during the decode phase, the newly generated tokens are immediately pushed to a channel. The Streaming Handler consumes these tokens, converts them back to text (detokenization), and pushes them to the client asynchronously over an SSE connection. By streaming the partial response in real-time, the user perceives a much lower latency (Time To First Token) compared to waiting for the entire generation to finish before sending an HTTP response.

**Why other options fail:**
- **A**: Streaming weights from disk is an offloading or unified memory strategy, not the role of the Streaming Token SSE Handler which sits between the model output and the API gateway.
- **C**: Distributing the KV cache across GPUs in a ring topology describes Ring Attention (or Sequence Parallelism), which is a model execution optimization, not an API response handler.
- **D**: While telemetry streaming is common in production systems, the "Streaming Handler" in the context of an LLM Inference Engine specifically refers to streaming the token responses back to the client to improve TTFT.
