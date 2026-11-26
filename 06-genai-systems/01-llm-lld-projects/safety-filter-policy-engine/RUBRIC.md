# Safety Filter & Policy Engine - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies moderation decisions, filter types, plugin architecture, and audit logging requirements. |
| Domain model quality | 25% | Clean abstraction of `PolicyEngine`, `ContentFilter`, `Rule`, `Policy`, `RuleViolation`, and `ModerationResult`. Uses appropriate patterns like Strategy and Chain of Responsibility. |
| Core logic & Extensibility | 25% | Correctly implements the filter chain where strictest action wins. Allows seamless addition of new filters without changing the core engine. |
| Advanced evaluation (v2) | 20% | Successfully models confidence-aware triage, calibrated routing, and preserves backwards compatibility with basic actions. |
| Testing & Correctness | 15% | Includes robust unit tests covering different filter scenarios, conflicting rules, edge cases (e.g., regex compilation), and v2 features. |

## Performance bands
- `1/5`: Monolithic evaluation function with hardcoded checks. Fails to separate filter logic from the engine.
- `3/5`: Separates filters but uses tight coupling or lacks a clear execution chain. Basic enum actions but no confidence routing or plugin extensibility.
- `5/5`: Clean Strategy and Chain of Responsibility patterns. Complete decoupling of engine and filters. Robust pre-compiled patterns, v2 calibrated routing, and high test coverage.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
