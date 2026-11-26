# Multi-Agent Orchestrator

## 📋 Problem Statement
In generative AI systems, complex tasks often exceed the capabilities of a single monolithic prompt or model call. A multi-agent orchestrator addresses this by decomposing tasks and routing them through specialized AI agents (e.g., Researcher, Coder, Reviewer). The core problem is to manage the state and control flow across these agents reliably, preventing infinite loops, preserving context between turns, and accurately determining when a consensus or final output has been reached.

## 🎯 Requirements

### Functional Requirements
1. **Supervisor Routing:** A central supervisor must be able to dispatch goals (public API `dispatch_goal(goal: str, max_turns: int = 10) -> OrchestrationResult`) to a starting agent and subsequently route messages dynamically based on agent responses. The implementation is verified by hand-checked normal/error test fixtures such as `test_supervisor_worker_handoff` and `test_cycle_detection`.
2. **Stateful Blackboard:** The system must maintain a shared `AgentState` containing an append-only `history` of all agent messages and a mutable `blackboard` dictionary for sharing arbitrary data (like research context or code drafts) across agents. Agents must implement the public API `process(message: AgentMessage, state: AgentState) -> AgentMessage`.
3. **Cycle Detection:** The orchestrator must detect infinite ping-pong loops between agents and terminate the execution if an identical message signature (sender, recipient, content) is observed more than once.
4. **Max-Turn Budget Termination:** The loop must enforce a hard upper bound on the number of agent turns to prevent runaway execution costs, returning a "Turn exhaustion" reason if the limit is reached before consensus.
5. **Consensus Evaluation:** Agents must be able to signal successful completion by returning a specific keyword (e.g., `CONSENSUS_REACHED`), which the supervisor evaluates to halt the loop and return the final result.

### Non-Functional Requirements
1. **Deterministic State Transitions:** The orchestration engine itself must be deterministic. While agent logic (like LLM calls) might be stochastic, the supervisor's loop, state tracking, and termination heuristics must behave predictably given the same sequence of messages.
2. **Timeout Handling:** Implicit in the max-turn budget is the requirement to bound execution time, ensuring the system does not hang indefinitely when an agent fails to yield a correct state transition.

## 🚀 Unimplemented Advanced Extensions (Clearly Labeled)
The following features are out of scope for the current baseline implementation, but represent natural extensions of the system:
- **Hierarchical agent topologies:** (Unimplemented Advanced Extension) Routing logic is currently flat; nested supervisors are not yet supported.
- **Human-in-the-loop review checkpoints:** (Unimplemented Advanced Extension) The system does not currently pause and await manual human authorization before continuing execution.
- **Async parallel tool calling:** (Unimplemented Advanced Extension) Agent processing is strictly sequential and synchronous.
