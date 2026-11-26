# Distributed Rate Limiting at Scale

## Overview

As systems scale to millions of requests per second (1M+ QPS), standard rate limiting algorithms and implementations begin to bottleneck. A naive approach of checking a centralized datastore (like Redis) on every single request introduces unacceptable latency, costs, and risks of cascading failures.

This document covers the evolution of rate limiting from basic algorithms to Tier-1 ultra-scale architectures, focusing on concurrency control, atomicity, and hybrid local-global token batching.

## Algorithm Comparison

### 1. Token Bucket
- **How it works**: Tokens are added to a bucket at a fixed rate. Each request consumes a token. If the bucket is empty, requests are dropped.
- **Pros**: Easy to understand, memory-efficient, allows bursts of traffic.
- **Cons**: Can cause burst-induced stampedes if not tuned properly.

### 2. Leaky Bucket
- **How it works**: Requests are added to a queue (the bucket). They are processed at a fixed, constant rate. If the queue is full, new requests are dropped.
- **Pros**: Smooths out traffic, producing a stable outflow rate.
- **Cons**: Bursts can fill the bucket with older requests, starving newer ones. Inflexible for bursty traffic.

### 3. Sliding Window Log
- **How it works**: Keeps a log of timestamps for every request. When a new request arrives, it removes outdated timestamps (older than the window) and checks if the remaining count exceeds the limit.
- **Pros**: Highly accurate, handles bursts and boundary conditions perfectly.
- **Cons**: High memory footprint (stores every timestamp) and computation cost per request. Not suitable for high QPS.

### 4. Sliding Window Counter (Cloudflare Approach)
- **How it works**: Divides time into fixed windows (e.g., 1 minute) and keeps a counter for each. To estimate the current rate, it interpolates the count from the previous window and the current window based on the overlap time.
  - **Cloudflare weighted interpolation formula**: 
    `Estimated Requests = (Previous Window Count * (1 - Elapsed % in Current Window)) + Current Window Count`
- **Pros**: **O(1) memory** (only stores two counters and their timestamps per user), highly efficient, smooths out the boundary issues of fixed windows.
- **Cons**: It is an approximation. It assumes traffic in the previous window was evenly distributed, which is typically a safe assumption at scale.

## The Concurrency Problem

In a distributed environment where multiple gateway instances handle requests for the same user, updating rate limit counters concurrently leads to race conditions.

### Concurrency Bugs in Get-Then-Set Pipelines
A naive implementation might read the current counter from Redis, increment it in application memory, and write it back:

1. Client A and Client B (different API gateways) receive requests for User X simultaneously.
2. Both read `User X count = 5`.
3. Both increment to 6.
4. Both write 6 back to Redis.
5. The actual count should be 7, but one request bypassed the limit unnoticed.

### Atomic Redis Lua Script Execution
To solve this, operations must be atomic. Redis is single-threaded, and executing a **Lua script** guarantees atomicity. The script reads the keys, applies the logic (e.g., checking if limits are exceeded, decrementing tokens, or updating counters), and writes the results back in one uninterruptible step.

```lua
-- Conceptual Lua script for a Token Bucket decrement
local tokens_key = KEYS[1]
local timestamp_key = KEYS[2]
-- ... logic to calculate replenishment ...
if current_tokens >= requested then
    redis.call("set", tokens_key, current_tokens - requested)
    return 1 -- Allowed
else
    return 0 -- Rejected
end
```

## Tier-1 Ultra-Scale Architecture (1M+ QPS)

While Redis Lua scripts solve concurrency, **hitting Redis on every request fails at scale**. A single Redis node can handle ~100k QPS. A Redis cluster can scale further, but the network round-trip time (RTT) for millions of requests adds immense latency and infrastructure cost.

### Gateway Local Memory Token Batching
To survive 1M+ QPS, we must decouple the request critical path from the central Redis store.

1. **Pre-fetching / Batching**: Instead of asking Redis for 1 token per request, the API Gateway asks for a batch (e.g., 100 tokens) at once.
2. **Local Consumption**: The Gateway stores these tokens in its local memory (e.g., Guava cache, ConcurrentHashMap). Subsequent requests for that user consume tokens from the local memory in sub-microsecond time.
3. **Background Async Replenishment**: When the local batch runs low (e.g., < 20%), an asynchronous background thread requests another batch from Redis. The critical path never blocks on a network call.

### Graceful Degradation during Redis Partition
If Redis goes down or a network partition occurs, the Gateways can gracefully degrade:
- **Fail Open**: Allow traffic to pass temporarily to preserve availability.
- **Local Rate Limiting Only**: Gateways can fall back to strictly enforcing a lower, local rate limit based on their fair share of the global limit (e.g., if Global Limit is 10k and there are 100 Gateways, enforce a local limit of 100).

This hybrid architecture (Local Memory + Global Redis) balances strict correctness with ultra-low latency and high availability.
