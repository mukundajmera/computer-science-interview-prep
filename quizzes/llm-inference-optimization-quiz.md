# LLM Inference Optimization Quiz

24 questions covering KV-cache memory calculation, PagedAttention, continuous batching, chunked prefill, speculative decoding, INT4/FP8 quantization, and FlashAttention-2.

### Question 1
What is the primary memory bottleneck during the autoregressive generation phase (decoding) of a Large Language Model?

A) The KV (Key-Value) Cache, which stores the key and value tensors for all previous tokens to avoid recomputing them
B) The model weights, which must be constantly swapped between CPU and GPU memory during generation
C) The feed-forward network (FFN) activations for the current token
D) The embedding lookup table, which scales linearly with the vocabulary size

### Question 2
How does PagedAttention solve the memory fragmentation issue associated with the KV Cache?

A) It breaks the KV Cache into fixed-size blocks (pages) that are allocated non-contiguously, similar to virtual memory in operating systems
B) It compresses the KV Cache using 4-bit quantization before storing it in VRAM
C) It offloads the KV Cache for inactive sequences to system RAM over PCIe
D) It dynamically resizes the self-attention heads based on available VRAM

### Question 3
In the context of LLM serving, what is 'Continuous Batching' (or iteration-level scheduling)?

A) Generating text in a continuous loop without returning control to the user
B) Batching the input prompts during the prefill phase, but processing the decoding phase sequentially
C) Continuously streaming the model weights from disk to GPU memory to support massive models
D) Injecting new requests into the batch as soon as a previous request finishes its generation, rather than waiting for the entire batch to complete

### Question 4
What is the primary benefit of Speculative Decoding?

A) It reduces the memory footprint of the KV Cache by predicting which tokens can be safely evicted
B) It allows the model to speculate on multiple different possible answers and present a tree of options to the user
C) It reduces the latency (Time Per Output Token) of autoregressive generation by using a smaller, faster model to draft multiple tokens which the large model verifies in parallel
D) It enables the model to bypass the prefill phase entirely by predicting the user's prompt

### Question 5
What is 'Chunked Prefill' and why is it used?

A) Splitting a very long input prompt into smaller chunks to prevent the prefill phase from causing long latency spikes for other requests concurrently generating tokens
B) Breaking the output generation into chunks of 100 tokens to stream to the user more smoothly
C) Dividing the model weights into chunks across multiple GPUs
D) Chunking the dataset during fine-tuning to fit into memory

### Question 6
How does FlashAttention-2 improve the performance of the self-attention mechanism compared to standard implementations?

A) It caches the final attention outputs on the disk to speed up subsequent requests
B) It skips calculating attention scores for tokens that are more than 1000 positions apart
C) It replaces the expensive Softmax function with a linear approximation
D) It minimizes memory reads and writes by keeping the attention computation entirely within the fast on-chip SRAM, avoiding round-trips to the slower HBM

### Question 7
When implementing Weight-Only Quantization (e.g., AWQ or GPTQ) at 4-bit, what happens during the actual matrix multiplication on the GPU?

A) The GPU performs the matrix multiplication natively using 4-bit arithmetic
B) The weights are kept in 4-bit in memory to save bandwidth, but are quickly dequantized to FP16 in the GPU registers just before the FP16 matrix multiplication occurs
C) The activations are also quantized to 4-bit, and integer arithmetic is used
D) The model relies entirely on the CPU to perform 4-bit math, bypassing the GPU

### Question 8
What is Tensor Parallelism (TP) in the context of LLM inference?

A) Splitting individual weight matrices (e.g., linear layers and attention heads) across multiple GPUs, so they collaboratively compute a single forward pass simultaneously
B) Splitting the sequence length so GPU 1 processes tokens 0-1000 and GPU 2 processes 1001-2000
C) Running identical copies of the model on different GPUs to handle more user requests concurrently
D) Splitting the model vertically, where GPU 1 handles layers 1-10 and GPU 2 handles layers 11-20

### Question 9
Which metric is the most appropriate for measuring the latency experienced by a user reading a streaming LLM response?

A) Total Generation Time
B) Time to First Token (TTFT) and Tokens Per Second (TPS)
C) Model loading time
D) GPU memory utilization percentage

### Question 10
What is the primary difference between the Prefill phase and the Decode phase in LLM inference?

A) The Prefill phase generates the first 50 tokens, and the Decode phase generates the rest
B) The Prefill phase runs on the CPU, while the Decode phase runs on the GPU
C) The Prefill phase processes the entire input prompt in parallel (compute-bound), while the Decode phase generates output tokens sequentially one-by-one (memory-bandwidth bound)
D) The Prefill phase updates the model weights based on the prompt, while the Decode phase reads the weights

### Question 11
Why does a larger batch size generally increase overall throughput (Tokens Per Second) but eventually increase Time Per Output Token (TPOT)?

A) Larger batches bypass the KV Cache entirely, which speeds up throughput but slows down TPOT.
B) Larger batches cause the model to generate fewer tokens per request, increasing overall throughput but penalizing individual requests.
C) Larger batches amortize the cost of loading model weights from memory across multiple requests, increasing throughput, but computing larger matrices eventually takes physical time in the Tensor Cores, slowing individual generation.
D) Larger batches trigger Speculative Decoding, which increases throughput but decoding verification slows down TPOT.

### Question 12
In the context of serving LLMs, what is prefix caching (or prompt caching)?

A) Caching the final textual output of the LLM in Redis so identical queries don't hit the GPU
B) Reusing the KV cache for common prompt prefixes (like system prompts or large context documents) across different user requests
C) Pre-computing the embeddings of the vocabulary and caching them in CPU RAM
D) Caching the router configurations to speed up API gateway latency

### Question 13
Which of the following scenarios is highly likely to cause an Out Of Memory (OOM) error on an inference server using naive static batching?

A) Receiving requests that all have identical system prompts
B) Deploying an INT8 model instead of an FP16 model
C) Serving a model using Tensor Parallelism across 8 GPUs
D) Receiving a batch of requests where one request has an extremely long prompt and another generates an extremely long response, forcing memory allocation for the maximum possible grid

### Question 14
How does KV Cache Offloading help when generating sequences that exceed the GPU's VRAM capacity?

A) It swaps inactive or older blocks of the KV cache from the GPU VRAM to the host CPU RAM via PCIe, retrieving them only when needed
B) It streams the KV cache to a cloud storage bucket (like S3) during inference
C) It deletes the oldest KV cache blocks permanently, relying on the model to infer missing context
D) It compresses the KV cache using gzip before storing it in VRAM

### Question 15
What is the fundamental difference between standard auto-regressive decoding and 'Medusa' style decoding?

A) Medusa forces the model to output Python code strictly using tree-search
B) Medusa uses a separate smaller model to draft tokens
C) Medusa modifies the attention mechanism to be bidirectional instead of causal
D) Medusa adds multiple extra decoding heads to the LLM to predict several future tokens simultaneously in a single forward pass, without needing a separate draft model

### Question 16
When calculating the Memory Bandwidth limit of a GPU for autoregressive generation, which factor dominates the Time Per Output Token (TPOT)?

A) The network latency between the client and the API gateway
B) The time it takes to compute the matrix multiplications in the Tensor Cores
C) The time it takes to read the entire model's weights from HBM to SRAM for every single generated token
D) The time it takes to read the input prompt embeddings from disk

### Question 17
What problem does 'Sliding Window Attention' (as used in Mistral) solve in the context of KV Cache memory?

A) It slides the model weights across multiple GPUs dynamically
B) It restricts the attention mechanism to only look back at the most recent N tokens, meaning the KV Cache never grows beyond N tokens in size
C) It restricts the user from typing more than N characters in the prompt window
D) It applies a convolution filter over the KV cache to smooth out noisy attention scores

### Question 18
Why is the FP8 data format gaining popularity over INT8 for LLM inference on newer hardware (like Hopper/H100)?

A) FP8 uses exactly 8 bits, whereas INT8 uses 9 bits in memory
B) FP8 mathematically prevents the model from generating hallucinations
C) FP8 is fully compatible with CPUs that lack specialized AI accelerators
D) FP8 provides a better dynamic range for representing outliers in activations and weights without the complex scaling factors required by integer quantization

### Question 19
In a distributed LLM deployment, what is the role of 'Pipeline Parallelism' (PP)?

A) Slicing individual weight matrices so GPUs can compute matrix multiplications collaboratively
B) Splitting the model layer-by-layer across multiple GPUs (e.g., layers 1-4 on GPU1, 5-8 on GPU2), passing the hidden states sequentially between them
C) Running identical copies of the model on different GPUs and routing user requests to the least busy one
D) Streaming the training data in a continuous pipeline to avoid disk I/O bottlenecks

### Question 20
What is the purpose of 'Ring Attention' in the context of extreme long-context inference?

A) It restricts attention to only the nearest neighbors in a circular graph architecture
B) It creates a circular KV Cache buffer that permanently loops to prevent Out of Memory errors
C) It distributes the context window (sequence length) across multiple GPUs in a ring topology, allowing the model to process sequences far larger than a single GPU's VRAM can hold
D) It allows the model to continuously generate tokens in an infinite loop for background processing tasks


### Question 21
When serving a Sparse Mixture of Experts (MoE) model (such as Mixtral 8x7B), how do its hardware requirements for inference compare to a dense model of the exact same total parameter count?

A) The MoE model significantly reduces the total VRAM capacity required to load the model weights, as only the active experts need to reside in GPU memory
B) The MoE model requires the same total VRAM capacity to store the weights, but significantly reduces the active compute (FLOPs) and memory bandwidth required per generated token
C) The MoE model increases the total VRAM capacity required due to the complex routing network, while the compute (FLOPs) per token remains identical to the dense model
D) The MoE model requires identical VRAM capacity and compute (FLOPs) as the dense model, but strictly prevents KV cache fragmentation


### Question 22
What is the primary optimization that "Flash-Decoding" introduces over standard FlashAttention for the decoding phase of long-context LLMs?

A) It compresses the KV cache into a 4-bit representation to reduce memory bandwidth bottlenecks during attention computation
B) It parallelizes the attention computation across the sequence length dimension of the KV cache, allowing multiple thread blocks to process different chunks of the past context simultaneously, which is critical when batch sizes are small and contexts are long
C) It replaces the exact Softmax attention with a sparse linear approximation to achieve O(N) complexity during autoregressive generation
D) It bypasses the attention mechanism entirely for the most recent 1000 tokens by caching the final FFN activations in SRAM

### Question 23
What is the primary advantage of using RadixAttention (as implemented in SGLang) for LLM inference?

A) It compresses the KV cache into a lower-precision format to save memory bandwidth during attention computation
B) It caches the KV cache in a radix tree structure, enabling efficient reuse of identical token prefixes across multiple requests to reduce prefill latency
C) It replaces the exact Softmax attention with a sparse linear approximation to achieve O(N) complexity during autoregressive generation
D) It parallelizes the attention computation across the sequence length dimension of the KV cache to speed up long-context generation

### Question 24
What is the primary function of the Streaming Handler in an LLM Inference Serving Engine?

A) To stream the model weights from the disk to the GPU dynamically, preventing Out Of Memory errors on large models
B) To receive tokens from the Worker Pool, detokenize them, and immediately stream Server-Sent Events (SSE) back to the client to minimize Time To First Token (TTFT)
C) To stream the KV cache across multiple GPUs in a ring topology for long context sequence parallelism
D) To continuously stream logs and telemetry metrics to an external monitoring cluster without blocking the main event loop
