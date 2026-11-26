# Multi-Agent Orchestrator

## 🚀 Follow-Ups (Optional Extensions)

The current baseline orchestrator proves the fundamental concepts of state management, routing, and termination bounds. The following features are strictly **optional, unimplemented extensions** that can be discussed as advanced follow-ups in an architectural interview setting.

### 1. Hierarchical Agent Topologies (Unimplemented)
**Concept:** The current implementation uses a flat routing registry—a single `SupervisorOrchestrator` routes messages sequentially between a `Researcher`, `Coder`, and `Reviewer`. As system complexity grows, a flat topology can become a routing bottleneck.
**Extension:** Implement nested supervisors. A top-level "Manager" orchestrator delegates sub-goals to lower-level specialized orchestrators (e.g., a "Code Base Supervisor" managing its own mini-loop of researchers, developers, and QA bots). This requires standardizing `BaseAgent` and `SupervisorOrchestrator` such that an orchestrator can recursively register as an agent inside another orchestrator.

### 2. Human-in-the-Loop Review Checkpoints (Unimplemented)
**Concept:** Currently, the system runs autonomously from `turn=1` to `max_turns` without stopping unless it hits a termination condition. For high-risk actions (e.g., executing code or dropping a database), human oversight is critical.
**Extension:** Introduce a checkpointing mechanism. If a `ReviewerAgent` flags a high-risk change, it halts execution, returning an intermediate state to the frontend UI. The system serializes the `AgentState` to a database and waits. A human operator reviews the change and manually injects a continuation message back into the orchestrator to resume the loop from the saved state.

### 3. Async Parallel Tool Calling (Unimplemented)
**Concept:** The orchestrator loop currently yields single messages sequentially (`agent.process(...)`). If a task requires calling five different APIs to gather research, it does so one at a time.
**Extension:** Implement a scatter-gather concurrency pattern. The `SupervisorOrchestrator` could dispatch a message to multiple worker agents simultaneously (e.g., using Python's `asyncio.gather()`). The results are awaited concurrently and then written to the thread-safe blackboard, drastically reducing overall latency for heavily I/O-bound parallelizable sub-tasks.
