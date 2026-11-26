# Safety Filter & Policy Engine - Common Pitfalls

## Common pitfalls
1. **Hardcoding rules or filter types:** Writing a massive `if-else` chain or embedding regex patterns directly inside the main `evaluate` loop rather than making rules and filters configurable entities.
2. **Missing a strict action hierarchy:** Failing to correctly aggregate moderation decisions (e.g., an `ALLOW` from one filter accidentally overwriting a `BLOCK` from another). The engine must enforce that the strictest action (e.g., `BLOCK > FLAG > ALLOW`) always takes precedence.
3. **Failing to maintain an audit trail:** Returning only a boolean or single enum without providing visibility into *why* the text was flagged (which rules matched, by which filter, with what severity).
4. **Poor latency characteristics with large rule sets:** Compiling regexes per-request or looping inefficiently through text rather than pre-compiling patterns and optimizing the O(n × r) evaluation time.
5. **Coupling the engine to specific model APIs or external calls:** Building a synchronous LLM call directly into a filter without an interface, making the policy engine slow and impossible to unit test independently.
6. **No support for context-aware policy sets:** Applying the same strictness to all use cases instead of grouping rules into swappable `PolicySet` configurations (e.g., strict for medical applications vs. relaxed for casual chat).

## Why these fail interviews
- **Breaks Non-Functional Requirements:** Hardcoding rules violates the Open-Closed Principle (OCP) and the requirement for a Plugin Architecture.
- **Lacks Production Readiness:** An engine that doesn't provide a detailed violation breakdown or an audit trail is unusable in a real-world moderation scenario where decisions must be appealed or analyzed.
- **Security & Safety Risks:** A flawed action hierarchy where a weak `ALLOW` overrides a critical `BLOCK` defeats the entire purpose of a safety filter.

## Mitigations
- **Use the Strategy Pattern:** Design a common `ContentFilter` interface that all concrete filters (e.g., `KeywordFilter`, `PIIFilter`) implement. The engine should only know about the interface.
- **Implement Enum Ordering:** Define `Action` and `Severity` as Enums with inherent comparison logic, ensuring `max()` operations correctly identify the strictest outcome across all filter results.
- **Return Rich Result Objects:** The `ModerationResult` should aggregate `RuleViolation` objects that detail the rule name, matched text, filter name, and severity.
- **Pre-compile Patterns:** Ensure that regex patterns within policies are compiled exactly once at system initialization or policy registration, not during content evaluation.
- **Decouple Policy Definition from Execution:** Group configurations into a `PolicySet` that the engine accepts dynamically during instantiation or evaluation, allowing runtime flexibility.

## Cross-links
- [GenAI Top Interview Pitfalls](../../PITFALLS.md)
- [GenAI Design Patterns](../../00-concepts/genai-design-patterns/README.md)
