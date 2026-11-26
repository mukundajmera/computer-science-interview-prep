# 💪 Strong Answer: LLM Inference Serving Engine

Use this guide to structure a strong interview response.

## 1. Framing the Problem

> **Say:** "Serving large language models is fundamentally different from serving traditional microservices. The bottleneck is rarely compute; it's memory bandwidth. To maximize throughput and minimize latency, we have to solve two main problems: efficiently batching requests that have unpredictable output lengths, and managing the massive memory footprint of the KV cache to prevent fragmentation."

## 2. High-Level Architecture

> **Say:** "My architecture consists of an API Gateway for tokenization and routing, a central Scheduler that implements continuous batching, a KV Cache Block Manager to handle memory via PagedAttention, and a distributed pool of GPU workers executing the model using tensor parallelism."

## 3. Deep Dive: Continuous Batching

> **Say:** "I will use continuous batching, or iteration-level scheduling, instead of static batching. Because requests generate varying numbers of tokens, static batching wastes GPU cycles waiting for the longest request to finish. In my design, as soon as a request emits a stop token, it is evicted from the batch, and a new request from the waiting queue is inserted for the very next iteration. This keeps the batch size consistently high."

## 4. Deep Dive: PagedAttention for KV Cache

> **Say:** "To solve KV cache memory fragmentation, I will implement a mechanism similar to OS virtual memory, called PagedAttention. Instead of allocating contiguous memory blocks based on maximum sequence length, I'll divide VRAM into fixed-size blocks (e.g., 16 tokens). The Block Manager maintains a block table for each request. As a sequence grows, new physical blocks are allocated dynamically. This virtually eliminates internal and external fragmentation, allowing us to fit significantly more requests into VRAM."

## 5. Handling Pre-fill vs. Decode Latency Spikes

> **Say:** "A common issue is that a new request requires a compute-heavy pre-fill phase, which can stall the memory-bound decode iterations of active requests, causing spikes in Inter-Token Latency. To mitigate this, I will implement chunked pre-fill. If a prompt is 10,000 tokens long, the scheduler splits it into chunks of 512 tokens. Each iteration processes one chunk alongside the decode tokens for active requests, ensuring that streaming latency remains smooth and predictable."

## 6. Closing Summary

> **Say:** "In summary, this inference engine maximizes throughput via continuous batching, eliminates memory waste using PagedAttention, and guarantees smooth streaming via chunked pre-fill. For models exceeding a single GPU's capacity, I've integrated tensor parallelism across the worker pool, allowing us to serve multi-billion parameter models at scale."
