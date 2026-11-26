# Multi-Agent Orchestrator

## 🏗️ Approach

This architecture solves the multi-agent execution problem by marrying three distinct design patterns into a cohesive deterministic loop.

### Design Patterns Utilized

1. **Supervisor-Worker Pattern:**
   The `SupervisorOrchestrator` acts as the single entry and exit point for external calls via the public API `dispatch_goal`. It encapsulates the control logic (looping, turn budgets, loop termination), while delegating the actual generative work to worker agents (`ResearcherAgent`, `CoderAgent`, `ReviewerAgent`) via their public API `process`. This separation of concerns means the supervisor never needs to know *how* to write code, and the coder never needs to manage the total execution budget. Hand-checked normal/error test fixtures such as `test_supervisor_worker_handoff` and `test_cycle_detection` verify this flow.

2. **Blackboard Pattern:**
   The `AgentState` acts as the blackboard. Complex generative tasks often require sharing multi-modal or highly nested data (like syntax trees, test output, or long-form research). Passing this strictly via linear message history becomes prohibitive for context windows. Instead, the `blackboard` dictionary allows any agent to read or write shared state (`research_data`, `code`, `review`), decoupling the agents from strict sequential dependencies.

3. **ReAct (Reason + Act) Loop Context:**
   The iterative loop from `turn=1` to `max_turns` simulates a reasoning execution cycle. Instead of a single model reasoning and acting, specialized sub-agents reason locally and route actions sequentially, mimicking a macro ReAct engine bounded by a strict budget.

### Cycle Detection Algorithm (Time O(1) per step, Space O(N) where N is number of steps)
The algorithm names and complexity describe the actual implementation, not an imagined production engine. A common failure mode in multi-agent systems is infinite ping-ponging (e.g., Coder generates bad code -> Reviewer requests a fix -> Coder generates the exact same bad code).
Our approach prevents this deterministically via a `seen_signatures` set.
On every turn, the orchestrator computes a unique signature tuple:
```python
msg_signature = (next_msg.sender, next_msg.recipient, next_msg.content)
```
If an identical signature is generated twice within the same orchestration session, the system immediately returns an `OrchestrationResult` with a "Cycle detected" failure reason. This ensures strict termination in cyclic failure topologies.

### State Serialization
To preserve a perfect, auditable trace of execution, `AgentState` separates the data into two structures:
1. **`history`:** A `typing.List[AgentMessage]` that tracks the exact conversational flow, step indices, and routing edges. This is highly useful for rendering front-end UI traces or for debugging the orchestration path.
2. **`blackboard`:** A `typing.Dict[str, typing.Any]` mapping string keys to arbitrary data objects.
Because `AgentMessage` objects are Python `dataclasses`, they are natively structured and easily serialized to JSON if this application needs to be deployed over REST/gRPC or persisted to a document database.

### Known Limitations and Strict Privacy Boundaries
Limitations and privacy boundaries are explicit:
- **Limitations:** The cycle detection algorithm uses strictly exact string/tuple equality (`(next_msg.sender, next_msg.recipient, next_msg.content)`). Semantic cycles (e.g., rephrasing the exact same feedback) are not caught. Expanding this would require fuzzy hashing or an LLM evaluator.
- **Privacy Boundaries:** The `blackboard` is entirely shared memory without partitioning. Any agent injected into the system has full read/write access to all data posted by any other agent. For production systems handling sensitive PII, the orchestrator must enforce strict role-based access control (RBAC) schemas on blackboard keys to maintain explicit privacy boundaries.
