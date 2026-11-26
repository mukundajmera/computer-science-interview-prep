# Prompt Builder - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies template variable substitution, partial formatting, escaping, role mapping, and token budget estimation. |
| Domain model quality | 25% | Clean abstraction of `PromptTemplate`, `Message`, `Role`, `PromptBuilder`, and partial binder. |
| Formatting & Validation | 25% | Strict missing-variable validation, safe interpolation without code injection vulnerabilities, token length guardrails. |
| Composition & Reusability | 20% | Supports composing sub-templates, system/user/assistant role separation, few-shot example formatting. |
| Extensibility & Tests | 15% | Uses Builder pattern, immutability where appropriate, clean unit tests with 100% path coverage, standard library only. |

## Performance bands
- `1/5`: Naive string concatenation or Python `.format()` without variable validation or role structure.
- `3/5`: Implements a basic PromptTemplate class, but lacks role-aware message formatting or partial binding.
- `5/5`: Fluent Builder API, strong variable validation, role-based chat formatting, few-shot formatting support, zero third-party deps.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
