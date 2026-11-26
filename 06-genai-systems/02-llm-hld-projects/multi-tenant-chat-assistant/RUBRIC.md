# Multi-Tenant Chat Assistant - Interview Scoring Rubric

A structured rubric for evaluating Multi-Tenant Chat Assistant system design interviews across several dimensions, capturing both GenAI and traditional HLD skills.

## Scoring Dimensions

| Dimension | Weight | Strong signal (What strong answers show) |
|---|---|---|
| Requirements & Scope | 10% | Proactively asks about multi-tenancy requirements, daily active users per tenant, latency constraints, cost limits, and safety/compliance expectations (PII, hate speech). Clarifies whether models are shared or dedicated per tenant. |
| Estimation & Cost Modeling | 10% | Methodically estimates token volume (input vs output), derives daily/monthly cost models per model tier, considers cache hit rates, and computes a latency budget (TTFT and generation). Understands model pricing differences. |
| API & Prompt Design | 15% | Defines versioned APIs that support streaming (SSE). Articulates a clear prompt assembly strategy merging platform rules, tenant-specific instructions, conversation history, and user input. Discusses A/B testing and prompt versioning. |
| Data Model & Isolation | 15% | Designs strong data isolation techniques (e.g., Row-Level Security in shared DB vs dedicated DBs for enterprise). Separates control plane (tenant configurations) from data plane (chat interactions). Uses appropriate databases for config (relational) and fast access (caching). |
| Architecture | 20% | Draws a complete, layered architecture: API Gateway (rate limiting, tenant resolution), Chat Orchestrator, Model Router, Safety Policy Engine, caching layers, and LLM backends. Demonstrates clear separation of platform vs per-tenant components. |
| Safety & Guardrails | 15% | Implements a robust two-layer safety system: mandatory platform guardrails + tenant-configurable policies. Employs inline (synchronous) checks for critical safety (toxicity) and understands the latency trade-offs involved. |
| Scalability & Resource Allocation | 10% | Addresses noisy neighbor problems via per-tenant rate limits, circuit breakers, and priority queues. Discusses tracking token budget utilization in real-time to prevent cost explosions. |
| Trade-offs & Communication | 5% | Communicates choices clearly, surfacing the cost-quality-latency triangle. Justifies decisions like Shared DB vs Dedicated DB, synchronous vs asynchronous safety checks, and shared model pool vs per-tenant deployments. |

## Performance bands

| Total Score | Rating | Recommendation | Description |
|---|---|---|---|
| 4.5 - 5.0 | 🟢 Strong Hire | Exceeds expectations | Demonstrates expert-level system design, deep understanding of GenAI cost/latency economics, and robust approaches to tenant isolation and safety guardrails. |
| 3.5 - 4.4 | 🟡 Hire | Solid fundamentals | Covers all main components effectively, correctly implements data isolation, and includes reasonable safety/cost controls, though may lack depth in edge cases or advanced optimizations. |
| 2.5 - 3.4 | 🟠 Lean No Hire | Acceptable basics | Understands basic CRUD operations and generic LLM calls but struggles with the complexities of multi-tenancy (noisy neighbors, RLS) or strict GenAI cost/latency/safety budgets. |
| < 2.5 | 🔴 No Hire | Significant gaps | Fails to design a secure multi-tenant system, ignores GenAI-specific constraints (token economics, streaming, safety), or cannot articulate clear trade-offs. |

## Cross-links

- [Problem Statement](./PROBLEM.md)
- [Design Document](./DESIGN.md)
- [Approach Document](./APPROACH.md)
