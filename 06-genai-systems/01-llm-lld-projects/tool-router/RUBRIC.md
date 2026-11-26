# Tool Router — Interview Scoring Rubric

Use this rubric to evaluate design quality and implementation thinking consistently for the Tool Router project.

> Related: [PROBLEM](./PROBLEM.md) · [APPROACH](./APPROACH.md) · [DESIGN](./DESIGN.md)

---

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Identifies error handling cases, schema validation needs, and middleware execution order. |
| Domain model quality | 25% | Clean abstractions for `ToolDefinition`, `ParameterSchema`, `ToolRouter`, `Middleware`, and execution results. |
| Routing & Validation | 25% | Robust mapping of tool names to handlers, correct argument extraction, and reliable parameter validation. |
| Error Handling & Metrics | 20% | Structured error responses, resilient handler invocation, and accurate tracking of execution time and call counts. |
| Extensibility & Tests | 15% | Easy addition of tools and middleware without modifying core logic, comprehensive tests for edge cases. |

## Performance bands

- `1/5`: Monolithic router class using large switch/if-else statements, no middleware support, poor error handling, missing schema validation.
- `3/5`: Basic tool registry implemented, but middleware might be tightly coupled or error handling and metric tracking are incomplete.
- `5/5`: Clean Open-Closed architecture for tools and middleware, comprehensive parameter validation, strong typing/schema definitions, and thorough unit tests.

## Cross-links

- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
