# Multi-Tenant Chat Assistant Platform - Common Pitfalls

## Common pitfalls
1. **Weak Tenant Isolation:** Implementing isolation strictly at the application layer without database-level guarantees (like Row-Level Security). If the application code misses a single `WHERE tenant_id = ?` clause, catastrophic cross-tenant data leakage occurs.
2. **Ignoring Noisy Neighbors & Token Budgets:** Failing to implement per-tenant rate limits or token budget enforcement in real-time. This allows one highly active tenant to consume all shared resources, degrading performance for others and driving up LLM API bills exponentially.
3. **Asynchronous Safety Checks:** Running safety filters on generated outputs asynchronously instead of blocking inline. This leads to inappropriate content being streamed to users before it can be caught, violating strict enterprise compliance rules.
4. **Poor Prompt Management:** Not allowing tenants to define their own system prompts, or failing to version these prompts. Without versioning, a bad prompt update can degrade assistant quality and cannot be easily rolled back.
5. **Lack of Tier-Based Model Routing:** Hardcoding the most capable, expensive model (e.g., GPT-4o) for all queries instead of routing based on tenant subscription tiers. This leads to inverted unit economics where basic-tier users cost more than they generate in revenue.
6. **No Platform-Level Safety Floor:** Allowing tenants to completely override safety policies without a non-negotiable platform-level safeguard. This exposes the platform provider to liability if a tenant configures their assistant to generate illegal or highly toxic content.

## Why these fail interviews
- **Breaks Data Privacy & Security:** Mishandling tenant isolation or safety policies in an enterprise B2B product is an immediate red flag. Security must be enforced deeply, not just at the UI or API layer.
- **Shows Lack of Operational Maturity:** Proposing systems without budget constraints, version control for configuration, or tiered resource allocation demonstrates inexperience with running multi-tenant SaaS platforms at scale.
- **Poor Unit Economics:** A design that doesn't consider the cost of LLM inference per tenant plan will result in a financially unviable platform.

## Mitigations
- **Database-Level Isolation:** Use PostgreSQL Row-Level Security (RLS) to enforce tenant isolation at the database engine level, ensuring all queries automatically filter by `tenant_id`.
- **Real-Time Usage Tracking:** Implement Redis-based token counters that update in real-time to enforce strict daily and monthly token budgets per tenant, returning HTTP 429 when limits are exceeded.
- **Inline Safety Policy Engine:** Implement a two-layer safety engine (mandatory platform layer + configurable tenant layer) that evaluates inputs and outputs synchronously before streaming tokens to the user.
- **Config Versioning & Caching:** Version all tenant system prompts and configurations in the database. Use Redis with pub/sub invalidation to cache configurations, enabling sub-second reads while supporting instant rollbacks.
- **Tier-Based Router:** Introduce a Model Router component that maps tenant plans to specific models (e.g., Basic -> GPT-4o-mini, Pro -> GPT-4o) and handles provider fallbacks.

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Design Document](DESIGN.md)
- [Approach & Trade-offs](APPROACH.md)
