# GenAI Inference Serving Flashcards

40 question-only flashcards for GenAI inference serving preparation.

Source alignment:
- [LLM Inference Serving Engine](../06-genai-systems/02-llm-hld-projects/llm-inference-serving-engine/DESIGN.md)
- [Streaming & KV-Cache](../06-genai-systems/00-concepts/streaming-kv-cache/)
- [Token / Cost / Latency Planning](../06-genai-systems/00-concepts/token-cost-latency/)

---

## Performance Metrics (5 Cards)

### Card 1
Front: What is Time to First Token (TTFT) and what phase of LLM inference primarily determines it?

### Card 2
Front: What is Inter-Token Latency (ITL) and how does it impact the user experience of a streaming response?

### Card 3
Front: How does the prefill phase differ from the decode phase in terms of compute vs. memory bandwidth boundedness?

### Card 4
Front: Why is total generation time not simply TTFT plus (Total Tokens * ITL) in practice?

### Card 5
Front: What is the relationship between batch size, throughput (tokens/sec), and Inter-Token Latency in LLM serving?

## Memory Management and KV Cache (10 Cards)

### Card 6
Front: What is the KV Cache in transformer inference and why is it necessary for autoregressive generation?

### Card 7
Front: How does memory fragmentation occur in traditional, statically allocated KV Cache management?

### Card 8
Front: What is PagedAttention and how does it solve the KV Cache fragmentation problem?

### Card 9
Front: How does PagedAttention enable efficient memory sharing for complex sampling techniques like beam search or parallel decoding?

### Card 10
Front: What is the formula to estimate the KV Cache memory size for a single token, given hidden dimension (h), number of layers (l), and precision bytes (b)?

### Card 11
Front: Why does processing long contexts often lead to Out-Of-Memory (OOM) errors even if the model weights fit comfortably in VRAM?

### Card 12
Front: What is KV Cache quantization (e.g., FP8, INT4 KV cache) and what are its trade-offs?

### Card 13
Front: How does Multi-Query Attention (MQA) or Grouped-Query Attention (GQA) reduce KV Cache size compared to Multi-Head Attention (MHA)?

### Card 14
Front: What is Prefix Caching (or Prompt Caching) and in what scenarios does it significantly improve TTFT?

### Card 15
Front: How do serving engines handle eviction when the KV Cache pool is fully utilized (e.g., recomputation vs. swapping to CPU)?

## Batching and Scheduling (8 Cards)

### Card 16
Front: What is static batching in LLM inference and why does it lead to poor GPU utilization?

### Card 17
Front: What is Continuous Batching (or In-Flight Batching) and how does it improve upon static batching?

### Card 18
Front: How does a continuous batching scheduler decide when to evict or preempt a sequence if VRAM is exhausted during generation?

### Card 19
Front: In continuous batching, how are the prefill phase of a new request and the decode phase of ongoing requests typically scheduled together?

### Card 20
Front: What is chunked prefill, and how does it help maintain low Inter-Token Latency when a new request with a very long prompt arrives?

### Card 21
Front: How does first-come-first-serve (FCFS) scheduling for LLM requests compare to shortest-job-first when sequence lengths are unknown in advance?

### Card 22
Front: What is the role of a tokenization / detokenization step in the serving pipeline, and why is it often offloaded to the CPU?

### Card 23
Front: How does the maximum sequence length limit impact the scheduling and admission control of incoming inference requests?

## Distributed Inference (Parallelism) (7 Cards)

### Card 24
Front: What is Tensor Parallelism (TP) in LLM serving, and why is it necessary for models like Llama-3 70B?

### Card 25
Front: How does communication overhead (e.g., All-Reduce operations) over NVLink impact latency in Tensor Parallelism?

### Card 26
Front: What is Pipeline Parallelism (PP), and how does it differ from Tensor Parallelism for serving large models?

### Card 27
Front: What is a "bubble" in Pipeline Parallelism, and how do serving engines attempt to minimize it?

### Card 28
Front: In a multi-node serving setup, why is Pipeline Parallelism often preferred across nodes while Tensor Parallelism is kept within a single node?

### Card 29
Front: What is Data Parallelism in the context of inference serving, and how does it compare to Tensor/Pipeline parallelism for throughput scaling?

### Card 30
Front: How does serving a Mixture of Experts (MoE) model change the VRAM requirements and compute characteristics compared to a dense model of the same total parameter count?

## Optimizations and Advanced Techniques (10 Cards)

### Card 31
Front: What is Speculative Decoding, and how does it reduce latency for autoregressive generation?

### Card 32
Front: In Speculative Decoding, what happens if the large "target" model rejects the tokens proposed by the small "draft" model?

### Card 33
Front: What is the difference between Weight-Only Quantization (e.g., AWQ, GPTQ) and Activation Quantization (e.g., SmoothQuant)?

### Card 34
Front: How does serving an INT8/INT4 quantized model affect memory bandwidth boundedness versus compute boundedness?

### Card 35
Front: What is FlashAttention, and how does it optimize the standard attention mechanism during the prefill phase?

### Card 36
Front: How does the choice of precision (FP16 vs. BF16) impact LLM inference serving?

### Card 37
Front: What are the primary bottlenecks (compute vs. memory bandwidth) when serving small batch sizes versus very large batch sizes?

### Card 38
Front: How does Structured Output generation (e.g., constrained JSON generation with guided decoding) impact inference latency?

### Card 39
Front: What is the trade-off of offloading model weights or KV cache to CPU RAM/PCIe in a low-resource serving environment?

### Card 40
Front: Why do modern serving engines (like vLLM or TGI) often use a custom OpenAI-compatible API gateway rather than direct RPC for external clients?
