# Agentic Workflow Orchestrator - Common Pitfalls

## Common pitfalls
1. **Synchronous Human-in-the-Loop Blocking:** Blocking an active thread, connection, or process while waiting for human approval. Since users may take minutes or even days to approve an action, this approach quickly leads to resource exhaustion and system crashes.
2. **Lack of Idempotency in Tool Execution:** Failing to account for network timeouts where a tool (e.g., sending an email, creating a calendar event) might have succeeded but the response was lost. Blindly retrying without idempotency keys leads to duplicate actions.
3. **Blind Retries on Semantic Failures:** Treating LLM parameter extraction errors or logical failures from tools (e.g., "invalid email format") the same as transient network errors (e.g., HTTP 503). Retrying the exact same bad payload blindly instead of prompting the LLM to correct its mistakes.
4. **In-Memory Task State:** Storing the workflow execution state (completed steps, intermediate outputs) purely in memory. If the executor node crashes or restarts mid-task, the progress is lost, violating durability and audit requirements.
5. **Coupling Planning with Execution:** Attempting to use a single monolithic LLM call to both generate the plan and immediately execute all steps, making it impossible to insert approval gates, recover effectively between steps, or scale execution concurrently.

## Why these fail interviews
- **Breaks Non-Functional Requirements:** Relying on in-memory state or synchronous blocking directly violates durability, availability, and throughput constraints.
- **Shows Lack of Distributed Systems Knowledge:** Missing idempotency handling is a classic red flag in system design interviews, especially when dealing with external API integrations.
- **Ignores GenAI-Specific Challenges:** Treating LLM hallucinated parameters or planning failures as standard software exceptions demonstrates a lack of practical experience with agentic systems.

## Mitigations
- **Asynchronous Workflows:** Use a durable queue, event-driven architecture, or a dedicated workflow engine (e.g., Temporal, AWS Step Functions) to suspend and resume task execution asynchronously upon receiving human approval.
- **Idempotency Keys and Checkpointing:** Persist execution state before and after invoking a tool. Always pass an idempotency key to external tool APIs to ensure exactly-once execution.
- **Semantic Error Recovery:** Differentiate between transient errors (retryable) and semantic errors. Feed semantic tool errors back into the LLM context so it can re-plan or correct its parameters.
- **Durable State Store:** Persist the task plan, step status, and intermediate outputs in a durable database (e.g., PostgreSQL, DynamoDB) at every state transition.
- **Decoupled Architecture:** Strictly separate the Planner (which uses the LLM to generate steps) from the Executor (which routes to tools and manages state). Generate a complete plan first, persist it, and then execute step-by-step.

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Design Architecture](./DESIGN.md)
- [GenAI Top Interview Pitfalls](../../PITFALLS.md)
