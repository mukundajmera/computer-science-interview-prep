# Agentic Workflow Orchestrator - Interview Scoring Rubric

Use this rubric to evaluate design quality and implementation thinking consistently for the Agentic Workflow Orchestrator project.

> Related: [PROBLEM](./PROBLEM.md) · [APPROACH](./APPROACH.md) · [DESIGN](./DESIGN.md)

---

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements & Scope | 10% | Clarifies the stateful nature of tasks, execution time (vs stateless chatbots), human-in-the-loop limits, and available tool set. |
| Back-of-Envelope Math | 10% | Estimates LLM call counts per task (planning + extraction + retry), storage needs for state and audit logs, and evaluates cost limits. |
| Workflow API & Models | 15% | Uses async/SSE APIs to handle human-in-the-loop latency. Solid DB schema handling state machine transitions, immutable audit logs. |
| Reliable Execution Engine | 25% | Proposes checkpointing (Temporal/SQS-like) per step. Addresses the retry mechanism (transient vs permanent) and limits infinite loops. |
| Exactly-Once Tool Calls | 20% | Detailed design for idempotency keys sent to the Tool Gateway. Clearly differentiates retryable errors from non-idempotent constraints. |
| GenAI Planning & Guardrails | 10% | Explicit separation of concerns (Planning LLM vs Extraction LLM). Defines JSON schema validation, parameter constraints, and fallback plans. |
| Trade-offs & Evaluation | 10% | Weighs Plan-then-Execute vs ReAct, Sync vs Async APIs, and Dedicated Agents vs Worker Pools with deep technical understanding. |

## Performance bands

- `1/5`: Trivial synchronous request/response chatbot design. Misses the durable workflow engine requirements. No idempotency or state checkpointing.
- `3/5`: Identifies the need for asynchronous execution and retry limits but lacks checkpointing on failures or a unified tool gateway. Basic idempotency concepts discussed.
- `5/5`: Elegant asynchronous, checkpoint-driven execution engine. Excellent handling of long-lived tasks, idempotent tool gateways, robust LLM schema validation, and complete audit logging.

## Cross-links

- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
