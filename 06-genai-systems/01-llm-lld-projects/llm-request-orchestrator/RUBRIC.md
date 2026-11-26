# LLM Request Orchestrator - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies multi-provider fallback, circuit breaking, retry strategies with exponential backoff, and rate limiting. |
| Domain model quality | 25% | Clean abstraction of `LLMProvider`, `Orchestrator`, `RetryPolicy`, `CircuitBreaker`, and response handlers. |
| Reliability & Fault tolerance | 25% | Correctly implements fallback cascades across providers, tracks error states, and trips circuit breakers on consecutive failures. |
| Streaming & Response handling | 20% | Supports streaming token generators and unified response envelopes regardless of underlying provider. |
| Extensibility & Tests | 15% | Uses Strategy pattern for providers and routing, mock provider with configurable latency and failures, zero external deps. |

## Performance bands
- `1/5`: Direct, hard-coded API call to a single model provider without retry or fallback mechanisms.
- `3/5`: Implements multiple providers, but lacks circuit breaker logic or proper exponential backoff retry.
- `5/5`: Robust resilience patterns (Circuit Breaker, Retry, Fallback cascade), cleanly decoupled provider abstraction, deterministic tests.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)