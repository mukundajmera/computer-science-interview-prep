# AI Safety Guardrails - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies guardrail types, action precedence, and tenant isolation. |
| Domain model quality | 25% | Clean abstraction of `GuardrailsEngine`, `ValidationContext`, `GuardrailResult`, and `GuardrailAction` enum. Uses appropriate orchestration and delegation to specific detector classes. |
| Core logic & Extensibility | 25% | Correctly implements fast-failing pre/post evaluations sequentially where the first BLOCK halts execution. Properly passes REDACTED text down the chain. Seamless addition of new guardrails. |
| Advanced evaluation (v2/v3) | 20% | Successfully models async parallel execution, tenant-specific policies, or semantic/telemetry features. |
| Testing & Correctness | 15% | Includes robust unit tests covering fast-failing, redaction cascades, and tenant isolation. |

## Performance bands
- `1/5`: Monolithic evaluation function with hardcoded checks. Fails to separate pre-execution from post-execution.
- `3/5`: Separates pre/post phases but struggles with passing modified state (redactions) down the chain. Basic tests but missing isolation.
- `5/5`: Clean orchestration. Complete decoupling of engine and guardrails. Handles tenant state flawlessly.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
