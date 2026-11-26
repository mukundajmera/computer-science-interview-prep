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
            # We will use this to ping pong with reviewer infinitely
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

class SupervisorOrchestrator:
    def __init__(self):
        self.agents: typing.Dict[str, BaseAgent] = {}
        self.state = AgentState()

    def register_agent(self, role: str, agent: BaseAgent):
        self.agents[role] = agent

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
        
        for turn in range(1, max_turns + 1):
            if current_msg.recipient == "supervisor":
                if current_msg.content == "CONSENSUS_REACHED":
                    return OrchestrationResult(True, current_msg.content, turn - 1, "Consensus")
                return OrchestrationResult(True, current_msg.content, turn - 1, "Success")
            
            if current_msg.recipient not in self.agents:
                return OrchestrationResult(False, current_msg.content, turn, f"Unknown recipient: {current_msg.recipient}")
                
            agent = self.agents[current_msg.recipient]
            next_msg = agent.process(current_msg, self.state)
            self.state.history.append(next_msg)
            
            msg_signature = (next_msg.sender, next_msg.recipient, next_msg.content)
            if msg_signature in seen_signatures:
                return OrchestrationResult(False, next_msg.content, turn, "Cycle detected")
            seen_signatures.add(msg_signature)
            
            if next_msg.content == "CONSENSUS_REACHED":
                return OrchestrationResult(True, next_msg.content, turn, "Consensus")
            
            current_msg = next_msg
            
        return OrchestrationResult(False, current_msg.content, max_turns, "Turn exhaustion")
