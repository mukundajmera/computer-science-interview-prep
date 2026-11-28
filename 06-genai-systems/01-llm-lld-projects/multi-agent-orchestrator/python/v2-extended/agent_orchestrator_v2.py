"""v2-extended multi-agent orchestrator.

Improvements over v1, each named by the project's own docs:
1. Semantic cycle detection (PITFALLS #1): v1 compares exact message
   tuples, so a reviewer that rephrases its rejection (e.g. appends a
   timestamp) slips past the check and burns the whole turn budget. v2
   also compares a normalized signature that strips volatile decoration
   (timestamps, case, whitespace), so decorated repeats of the same
   rejection halt as cycles.
2. Per-agent retries (spec follow-up): an agent that raises a
   TransientAgentError is retried in place up to max_retries instead of
   crashing the run; retries do not consume turns.
3. Content budget (PITFALLS #3): the supervisor tracks cumulative
   message payload size and halts with "Budget exhausted" when the run
   exceeds max_budget_chars, so context growth is bounded by policy
   rather than by the turn count alone.
"""
import re
import typing
from dataclasses import dataclass, field


@dataclass
class AgentMessage:
    sender: str
    recipient: str
    role: str
    content: str
    step_index: int


@dataclass
class AgentState:
    history: typing.List[AgentMessage] = field(default_factory=list)
    blackboard: typing.Dict[str, typing.Any] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    success: bool
    final_result: str
    turns_used: int
    reason: str
    retries_used: int = 0


class TransientAgentError(Exception):
    """An agent failure worth retrying (rate limit, flaky tool call)."""


class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        raise NotImplementedError


class ResearcherAgent(BaseAgent):
    def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        research_data = f"Research data for: {message.content}"
        state.blackboard['research_data'] = research_data

        return AgentMessage(
            sender=self.name,
            recipient="coder",
            role=self.role,
            content=research_data,
            step_index=message.step_index + 1
        )


class CoderAgent(BaseAgent):
    def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        research = state.blackboard.get('research_data', '')

        if "cycle_trigger" in message.content:
            code = "bad_code"
        elif "max_turns_trigger" in message.content:
            turn_count = state.blackboard.get('turn_count', 0) + 1
            state.blackboard['turn_count'] = turn_count
            code = f"max_turns_trigger_{turn_count}"
        elif "max_turns_trigger" in research:
            turn_count = state.blackboard.get('turn_count', 0) + 1
            state.blackboard['turn_count'] = turn_count
            code = f"max_turns_trigger_{turn_count}"
        else:
            code = f"Code implementation using {research}"

        state.blackboard['code'] = code

        return AgentMessage(
            sender=self.name,
            recipient="reviewer",
            role=self.role,
            content=code,
            step_index=message.step_index + 1
        )


class ReviewerAgent(BaseAgent):
    def process(self, message: AgentMessage, state: AgentState) -> AgentMessage:
        code = state.blackboard.get('code', '')

        if code == "bad_code":
            return AgentMessage(
                sender=self.name,
                recipient="coder",
                role=self.role,
                content="cycle_trigger",
                step_index=message.step_index + 1
            )
        elif "max_turns_trigger" in code:
            return AgentMessage(
                sender=self.name,
                recipient="coder",
                role=self.role,
                content=f"max_turns_trigger_{code}",
                step_index=message.step_index + 1
            )
        elif "CONSENSUS" in message.content or "CONSENSUS" in code:
            return AgentMessage(
                sender=self.name,
                recipient="supervisor",
                role=self.role,
                content="CONSENSUS_REACHED",
                step_index=message.step_index + 1
            )
        else:
            state.blackboard['review'] = "Approved"
            return AgentMessage(
                sender=self.name,
                recipient="supervisor",
                role=self.role,
                content="Code approved",
                step_index=message.step_index + 1
            )


_TIMESTAMP_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}([tT ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(z|[+-]\d{2}:?\d{2})?)?"
    r"|\d{1,2}:\d{2}(:\d{2})?(\s*(am|pm|AM|PM))?"
)
_WS_RE = re.compile(r"\s+")


def normalize_content(content: str) -> str:
    """Strips the volatile decoration PITFALLS #1 names: timestamps,
    letter case and whitespace runs. Deliberately keeps digits that are
    not part of a timestamp, so a counter-based ping-pong
    (max_turns_trigger_1, _2, ...) still reads as distinct messages and
    is bounded by turn exhaustion rather than mis-flagged as a cycle."""
    no_ts = _TIMESTAMP_RE.sub("", content)
    return _WS_RE.sub(" ", no_ts).strip().lower()


class SupervisorOrchestratorV2:
    def __init__(self, max_retries: int = 2, max_budget_chars: typing.Optional[int] = None):
        self.agents: typing.Dict[str, BaseAgent] = {}
        self.state = AgentState()
        self.max_retries = max_retries
        self.max_budget_chars = max_budget_chars

    def register_agent(self, role: str, agent: BaseAgent):
        self.agents[role] = agent

    def _process_with_retries(self, agent: BaseAgent, message: AgentMessage) -> typing.Tuple[AgentMessage, int]:
        attempts = 0
        while True:
            try:
                return agent.process(message, self.state), attempts
            except TransientAgentError:
                attempts += 1
                if attempts > self.max_retries:
                    raise

    def dispatch_goal(self, goal: str, max_turns: int = 10) -> OrchestrationResult:
        self.state = AgentState()

        if not self.agents:
            return OrchestrationResult(False, "", 0, "No agents registered")

        start_role = "researcher" if "researcher" in self.agents else list(self.agents.keys())[0]

        current_msg = AgentMessage(
            sender="supervisor",
            recipient=start_role,
            role="supervisor",
            content=goal,
            step_index=0
        )
        self.state.history.append(current_msg)

        seen_signatures = set()
        seen_semantic_signatures = set()
        retries_used = 0

        for turn in range(1, max_turns + 1):
            if current_msg.recipient == "supervisor":
                if current_msg.content == "CONSENSUS_REACHED":
                    return OrchestrationResult(True, current_msg.content, turn - 1, "Consensus", retries_used)
                return OrchestrationResult(True, current_msg.content, turn - 1, "Success", retries_used)

            if current_msg.recipient not in self.agents:
                return OrchestrationResult(False, current_msg.content, turn, f"Unknown recipient: {current_msg.recipient}", retries_used)

            agent = self.agents[current_msg.recipient]
            try:
                next_msg, attempts = self._process_with_retries(agent, current_msg)
            except TransientAgentError:
                return OrchestrationResult(False, current_msg.content, turn,
                                           f"Agent failure after {self.max_retries} retries: {current_msg.recipient}",
                                           retries_used + self.max_retries)
            retries_used += attempts
            self.state.history.append(next_msg)

            msg_signature = (next_msg.sender, next_msg.recipient, next_msg.content)
            if msg_signature in seen_signatures:
                return OrchestrationResult(False, next_msg.content, turn, "Cycle detected", retries_used)
            seen_signatures.add(msg_signature)

            semantic_signature = (next_msg.sender, next_msg.recipient, normalize_content(next_msg.content))
            if semantic_signature in seen_semantic_signatures:
                return OrchestrationResult(False, next_msg.content, turn, "Cycle detected (semantic)", retries_used)
            seen_semantic_signatures.add(semantic_signature)

            if next_msg.content == "CONSENSUS_REACHED":
                return OrchestrationResult(True, next_msg.content, turn, "Consensus", retries_used)

            if self.max_budget_chars is not None:
                total_chars = sum(len(m.content) for m in self.state.history)
                if total_chars > self.max_budget_chars:
                    return OrchestrationResult(False, next_msg.content, turn, "Budget exhausted", retries_used)

            current_msg = next_msg

        return OrchestrationResult(False, current_msg.content, max_turns, "Turn exhaustion", retries_used)
