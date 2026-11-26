# LLM Request Orchestrator - Follow-Up Questions

## Follow-up questions
1. How do you implement semantic caching in front of multi-provider orchestration?
2. How would you handle dynamic cost-based routing (e.g. cheapest provider meeting latency SLA)?
3. How do you implement load-shedding and priority queues for Tier-1 vs free users?
4. How do you handle token rate limit tracking (RPM vs TPM) across distributed instances?
5. How would you support structured JSON schema outputs reliably across different model providers?

## Variants and extensions
- Adaptive routing based on live moving-average latency.
- Speculative decoding / parallel provider racing with first-token cancellation.
- Token bucket distributed rate limiter with Redis.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Design details](./DESIGN.md)
