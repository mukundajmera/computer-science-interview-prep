# Multi-Agent Orchestrator

## 📝 Rubric

The following rubric provides candidate-created guidance for grading an orchestrator implementation. This is not an official company scorecard, but rather a reference for observable dimensions and performance signals.

| Dimension | 1-2 (Needs Improvement) | 3 (Meets Bar) | 4-5 (Strong/Exceptional) |
| --- | --- | --- | --- |
| **Architecture & Structure** | Orchestration logic is tightly coupled with agent logic (e.g., agents calling each other directly without a supervisor). Missing blackboard pattern or message envelope structure. | Implements a central `SupervisorOrchestrator` acting as the ReAct loop engine. Agents implement a common `BaseAgent` interface. Clear separation of `history` and `blackboard` in `AgentState`. | Highly decoupled. Supervisor logic is completely independent of specific agent implementations. Clean, immutable `AgentMessage` design. Blackboard keys are well-defined and predictably scoped. |
| **Safety & Loop Bounds (Correctness)** | Vulnerable to infinite loops. Lacks cycle detection or a maximum turn budget. System hangs if an agent continually responds with bad output. | Enforces a `max_turns` budget (causing `Turn exhaustion`) to bound execution. Implements basic cycle detection to halt on redundant loops (e.g., checking if `(sender, recipient, content)` matches any in a `seen_signatures` set). | Exhaustive safety invariants. Differentiates clearly between deterministic loop failures (`Cycle detected`, `Turn exhaustion`) and success. Gracefully handles unparseable agent responses or missing registry roles. |
| **State Consistency & Consensus** | Blackboard state is overwritten destructively or race conditions exist (in async models). System fails to halt correctly when agents reach agreement. | Maintains an append-only `history` of `AgentMessage` objects. Detects early termination when a consensus keyword like `CONSENSUS_REACHED` is returned to the supervisor. | Perfect state serializability. `AgentState` is easily exportable (e.g., for front-end rendering or debugging). Precise tracking of sequence depth via `step_index`. Demonstrates deep understanding of shared memory vs. message passing tradeoffs. |

### Key Code Invariants to Validate
- **Unknown Recipient:** The orchestrator checks `if current_msg.recipient not in self.agents`. If true, execution halts with `f"Unknown recipient: {current_msg.recipient}"`.
- **Cycle Detection:** A `msg_signature` containing `(next_msg.sender, next_msg.recipient, next_msg.content)` is generated and checked against a `seen_signatures` set. If found, execution halts with `"Cycle detected"`.
- **Max Turn Budget:** The loop from `1` to `max_turns` terminates with a `"Turn exhaustion"` reason if the budget is reached before consensus.
- **Consensus Handling:** The supervisor actively checks if `next_msg.content == "CONSENSUS_REACHED"` to gracefully return success and halt early.
