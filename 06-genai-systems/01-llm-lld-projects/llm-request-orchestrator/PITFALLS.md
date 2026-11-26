# LLM Request Orchestrator - Common Pitfalls

## Common pitfalls
1. Thundering herd problem on upstream providers during outages without jitter in retry backoffs.
2. Inconsistent response formats across different provider adapters leaking provider-specific details.
3. Sticking to a failing primary provider when errors are deterministic (e.g. prompt too long or 400 Bad Request) vs transient (503 Service Unavailable).
4. Leaking sensitive credentials or prompts in failure logs.
5. Inability to cancel in-flight streaming requests when client disconnects.

## Why these fail interviews
- Reveals a lack of production experience with real-world LLM provider rate limits, outages, and cost spikes.
- Shows poor failure classification (retrying non-retriable client errors).

## Mitigations
- Classify errors into retriable (transient, 429, 503) vs non-retriable (validation, 400).
- Add full jitter to exponential backoff delays.
- Enforce strict unified response interfaces across all provider adapters.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Design details](./DESIGN.md)
