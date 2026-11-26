# Multi-Agent Orchestrator

## ⚠️ Pitfalls

When designing and extending multi-agent systems, several common pitfalls can derail execution reliability and performance.

### 1. Infinite Agent Ping-Pong (Strict Cycles vs. Semantic Cycles)
**The Pitfall:** Agents get trapped in an endless loop of rejecting and retrying the same incorrect output, draining the turn budget without making progress.
**Concrete Counterexample:** In the current implementation, if the `coder` produces code labeled `"bad_code"`, the `reviewer` explicitly responds with the exact string `"cycle_trigger"`, which in turn causes the `coder` to produce `"bad_code"` again. 
**Current Mitigation:** The system computes an exact tuple `(next_msg.sender, next_msg.recipient, next_msg.content)` and checks it against a `seen_signatures` set, immediately halting with `"Cycle detected"`.
**Remaining Vulnerability:** Because the check relies on *exact string equality*, it is blind to semantic cycles. If the `reviewer` slightly alters the rejection text each time (e.g., appending a timestamp or rephrasing), the string equality check fails, the loop bounds are not triggered early, and the system continues ping-ponging until it hits `"Turn exhaustion"`.

### 2. Blackboard Race Conditions (Async Environments)
**The Pitfall:** If agents were extended to operate in parallel, multiple agents writing to the shared `blackboard` concurrently could cause race conditions.
**Concrete Counterexample:** A concurrent `coder_a` and `coder_b` both try to read `state.blackboard['turn_count']`, increment it, and write it back. Without a mutex lock or thread-safe atomic operations on the dictionary, the updates will overwrite each other destructively.
**Current Mitigation:** The existing baseline implementation is strictly sequential and synchronous. The `SupervisorOrchestrator` only processes one `current_msg` and dispatches to one `agent` at a time, so no race conditions exist. If parallel tool calling or async agent processing is added (optional extension), the blackboard dictionary must become thread-safe.

### 3. Unbounded Context Explosion
**The Pitfall:** Storing massive amounts of generated data directly in the linear `history` array can quickly exceed the context window limits of an LLM.
**Concrete Counterexample:** If a `researcher` agent downloads a 10MB CSV file, passing that 10MB payload directly inside `content` via the message routing `history` would bloat the prompt and cause an immediate token limit exception.
**Current Mitigation:** The `blackboard` pattern is utilized so that bulky artifacts (`research_data`, `code`, `review`) can be stored centrally by reference. The message `history` remains lightweight, acting primarily as a routing envelope (e.g., passing `"Research data for: <topic>"`).
