# AI Safety Guardrails - Common Pitfalls

## Common pitfalls
1. **Missing fast-failing mechanics:** Evaluating all guardrails even after one has returned a `GuardrailAction.BLOCK`, wasting computation time and potentially sending blocked input to the LLM.
2. **Leaking tenant state:** Storing request-specific data or redaction patterns as mutable instance variables in a guardrail singleton, leading to race conditions or cross-tenant data leaks. All request data must stay in the `ValidationContext`.
3. **Failing to propagate GuardrailAction.REDACT:** A PII redactor removes a sensitive string, but the engine accidentally passes the *original* input, defeating the purpose.
4. **Hallucinating standard library features:** Attempting to use Python's `threading.RLock` or Java's `ConcurrentHashMap` where simple atomic operations or immutable context objects are sufficient for the baseline implementation.

## Why these fail interviews
- **Lacks Production Readiness:** An engine that doesn't fast-fail will cause catastrophic latency spikes in production.
- **Security & Privacy Risks:** Leaking state across tenants or failing to pass redacted strings are critical security vulnerabilities.

## Mitigations
- **Implement Pipeline Fast-Failing:** Evaluate guardrails sequentially and immediately `return` if any result action is `GuardrailAction.BLOCK`.
- **Stateless Guardrails:** Design guardrails to only rely on their `evaluate(text, context)` parameters.
- **Update Working State:** Reassign the working text variable whenever a guardrail returns a `GuardrailAction.REDACT` and a `modified_text`.

## Cross-links
- [GenAI Top Interview Pitfalls](../../PITFALLS.md)
- [GenAI Design Patterns](../../00-concepts/genai-design-patterns/README.md)
