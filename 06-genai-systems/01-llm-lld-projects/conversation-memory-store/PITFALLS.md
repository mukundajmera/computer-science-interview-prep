# Common pitfalls and mitigation strategies

## Common pitfalls
1. Unbounded buffer memory growth leading to OOM or context window exhaustion.
2. Inaccurate token budgeting due to naive character slicing instead of token/word estimation.
3. Leaking conversation history across different user sessions or tenants.
4. Loss of critical system instructions when sliding window evicts early messages.
5. Inconsistent conversation state when branching/forking without deep-copying messages.
6. Synchronous, blocking summarization in the request path causing latency spikes.

## Why these fail interviews
- Demonstrates lack of production awareness regarding LLM token context limits.
- Violates multi-tenant isolation and security principles.
- Poor architectural separation between storage, retrieval, and compression.

## Mitigations
- Enforce strict TokenLimitedMemory and WindowMemory caps.
- Retain SystemMessage pin-at-head across all eviction policies.
- Deep copy message lists on conversation fork.
- Pluggable asynchronous background summarization.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Design details](./DESIGN.md)
