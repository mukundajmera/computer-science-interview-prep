# AI Coding Copilot - Interview Scoring Rubric

Use this rubric to evaluate design quality and implementation thinking consistently for the AI Coding Copilot project.

> Related: [PROBLEM](./PROBLEM.md) · [APPROACH](./APPROACH.md) · [DESIGN](./DESIGN.md)

---

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements & Scope | 10% | Distinguishes between fast-path (inline completion) and slow-path (chat). Identifies ultra-low latency constraints (<300ms) for completion and high context needs for chat. |
| Back-of-Envelope Math | 10% | Estimates token generation speed, user request concurrency (typing events vs explicit chat), network round-trip limits, and inference cost scaling. |
| IDE Context Engineering | 20% | Designs a robust client-side debouncer and context collector. Handles limited context windows intelligently by ranking local files, imports, and cursor position (Fill-in-the-Middle). |
| Dual-Path Architecture | 20% | Clearly separates the architecture into a Fast Path using smaller, highly-optimized models (e.g., CodeLlama, Codestral) and a Rich Path using larger reasoning models (e.g., GPT-4). |
| Latency Optimization | 20% | Proposes streaming responses, KV cache reuse, specialized hardware (e.g., vLLM/TGI), and speculative decoding. Discusses geographic load balancing and edge inference if applicable. |
| Telemetry & Feedback | 10% | Designs tracking for ghost-text acceptance/rejection. Handles asynchronous telemetry data ingestion without blocking the critical path. |
| Trade-offs & Evaluation | 10% | Weighs client-side vs server-side context ranking, single-tenant vs multi-tenant model hosting, and cost vs latency vs quality trade-offs. |

## Performance bands

- `1/5`: Treats the system as a simple wrapper around a generic LLM API. Does not address the ultra-low latency requirements of inline completion or the Fill-in-the-Middle (FIM) pattern.
- `3/5`: Identifies the need for dual paths and low latency, but struggles with context window limits, IDE integration details, or how to practically achieve sub-300ms response times globally.
- `5/5`: Elegant dual-path architecture with deep understanding of IDE debouncing, FIM context building, inference latency optimizations (vLLM, KV caching), and a robust telemetry feedback loop.

## Cross-links

- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
