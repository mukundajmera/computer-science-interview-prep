# Multi-Agent Orchestrator

## 🎨 Design

### Entities and Class Hierarchy
- **`BaseAgent`**: An abstract base class that defines the core identity (`name`, `role`) and a public API `process(message: AgentMessage, state: AgentState) -> AgentMessage` method interface that must be implemented by all concrete agents.
- **`ResearcherAgent`**: Simulates information retrieval. Extracts data based on the goal, saves it to the blackboard, and routes to the `coder`.
- **`CoderAgent`**: Simulates code generation. Reads research from the blackboard, creates code, saves it to the blackboard, and routes to the `reviewer`. Also contains logic for simulating failure states (cycles and max turns).
- **`ReviewerAgent`**: Simulates code validation. Reads code from the blackboard. It can route back to the `coder` with fixes (ping-ponging), or route to the `supervisor` with an approval or a `CONSENSUS_REACHED` flag.
- **`SupervisorOrchestrator`**: The central engine (public API `dispatch_goal(goal: str, max_turns: int = 10) -> OrchestrationResult`). It maintains a registry of initialized agents, holds the shared `AgentState`, and manages the ReAct loop to route messages between agents until a termination condition is met.

### Blackboard State Schema
The state passed to every agent is encapsulated in the `AgentState` dataclass:
- **`history`**: A `typing.List[AgentMessage]` that provides an append-only log of every step taken.
- **`blackboard`**: A `typing.Dict[str, typing.Any]` used as shared memory. The Researcher writes `research_data`, the Coder writes `code`, and the Reviewer writes `review`. It acts as a mutable KV store for artifacts.

### Agent Message Envelope
Inter-agent communication is strictly formatted using the `AgentMessage` dataclass:
- **`sender`**: The string role/name of the transmitting agent.
- **`recipient`**: The string role/name of the target agent.
- **`role`**: Contextual role of the sender.
- **`content`**: The actual payload (e.g., prompt, code, feedback).
- **`step_index`**: Monotonically increasing integer tracking the sequence depth.

### Turn Loop Algorithm
The core orchestrator loop runs iteratively up to a defined `max_turns` budget:
1. Initialize the loop with a starting message from the `supervisor` to the first registered agent.
2. Iterate `turn` from 1 to `max_turns`.
3. **Consensus Check:** If the current message recipient is `"supervisor"`, the orchestrator inspects the content. If it matches `CONSENSUS_REACHED`, the loop halts successfully. Otherwise, it halts successfully with the final text.
4. **Validation Check:** Ensure the recipient exists in the agent registry.
5. **Agent Processing:** Retrieve the target agent and invoke `agent.process(current_msg, self.state)`.
6. **State Update:** Append the resulting `next_msg` to `state.history`.
7. **Cycle Detection:** Compute a signature `(next_msg.sender, next_msg.recipient, next_msg.content)`. If this signature exists in `seen_signatures`, halt the loop immediately with a `"Cycle detected"` failure. Otherwise, add it to the set.
8. **Forward Consensus Check:** If `next_msg.content` equals `CONSENSUS_REACHED`, halt the loop immediately as a success.
9. **Advance Turn:** Set `current_msg = next_msg` and repeat.
10. If the loop completes without early termination, return a `"Turn exhaustion"` failure.

### Sequence Flow
```text
1. Supervisor --(dispatch goal)--> ResearcherAgent
2. ResearcherAgent --(writes research to blackboard, creates message)--> CoderAgent
3. CoderAgent --(reads research, writes code, creates message)--> ReviewerAgent
4. ReviewerAgent (Option A) --(approves code)--> Supervisor (Success)
   ReviewerAgent (Option B) --(rejects code)--> CoderAgent (Ping-pong)
   ReviewerAgent (Option C) --(CONSENSUS_REACHED)--> Supervisor (Consensus Success)
```

### Normal / Error Fixtures from Implementation
Hand-checked normal/error test fixtures in `test_agent_orchestrator.py` manually verify the control flow with specific scenarios:
- **Normal Path:** `test_supervisor_worker_handoff()` dispatches the goal `"Build a web server"`. The loop advances 4 times: `supervisor -> researcher -> coder -> reviewer`. The `reviewer` agent sets `blackboard['review'] = "Approved"`, returning `"Code approved"`, halting with success.
- **Error Path (Cycle):** `test_cycle_detection()` dispatches `"cycle_trigger"`. The `coder` sets code to `"bad_code"`, causing the `reviewer` to reply with `"cycle_trigger"`. The system computes the matching `msg_signature` tuple in the `seen_signatures` set, and terminates with reason `"Cycle detected"`.

### Algorithm Complexities
The complexities describe the actual implementation, not an imagined production engine:
- **Time Complexity:** O(N) where N is the number of turns executed (bounded by `max_turns`).
- **Space Complexity:** O(N) where N is `max_turns`. The `history` list grows linearly, and Cycle Detection Space is O(N) since `seen_signatures` stores up to N items.

### Limitations and Privacy Boundaries
Limitations and privacy boundaries are explicit:
- **Synchronous Execution:** Agents run sequentially.
- **Cycle Detection:** Relies on exact string match; semantic cycles are not caught.
- **No Isolation:** Agents share the `blackboard` with no strict memory isolation.
- **Simulation Only:** Uses hand-coded simulated agents without real LLM API calls.

### State Machine Diagram
The state transitions are formalized in the Mermaid diagram below:

[Orchestrator State Machine Diagram](diagrams/orchestrator-state-machine.mmd)
