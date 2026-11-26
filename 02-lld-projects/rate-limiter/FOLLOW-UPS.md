# Rate Limiter - Follow-Up Questions

## Follow-up questions
1. How would you implement weighted permit consumption without breaking old APIs?
2. How would you protect against hot-key amplification at the gateway layer?
3. How would you roll out policy changes safely across rolling deploys?
4. How would you design hybrid fail-open/fail-closed modes per endpoint tier?
5. How would you validate limiter fairness and false-throttle rates in production?

## Variants and extensions
1. Tenant-aware quota hierarchies with inherited defaults.
2. Regional rate limits with reconciliation lag tolerances.
3. Adaptive rate limits driven by error budget or SLO pressure.
4. Pre-flight quota simulation endpoint for clients.

## Interviewer probes to prepare
- "What is the atomic unit of decision in your limiter?"
- "Where do you store state if this becomes distributed?"
- "How do you avoid noisy-neighbor starvation?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
