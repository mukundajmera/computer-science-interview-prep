import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from agent_orchestrator import (
    SupervisorOrchestrator,
    ResearcherAgent,
    CoderAgent,
    ReviewerAgent,
    AgentState,
    AgentMessage
)

def test_supervisor_worker_handoff():
    orchestrator = SupervisorOrchestrator()
    orchestrator.register_agent("researcher", ResearcherAgent("res1", "researcher"))
    orchestrator.register_agent("coder", CoderAgent("cod1", "coder"))
    orchestrator.register_agent("reviewer", ReviewerAgent("rev1", "reviewer"))
    
    result = orchestrator.dispatch_goal("Build a web server")
    
    assert result.success is True
    assert result.reason == "Success"
    assert "Code approved" in result.final_result
    assert len(orchestrator.state.history) == 4 # start -> res -> cod -> rev

def test_max_turns_termination():
    orchestrator = SupervisorOrchestrator()
    orchestrator.register_agent("researcher", ResearcherAgent("res1", "researcher"))
    orchestrator.register_agent("coder", CoderAgent("cod1", "coder"))
    orchestrator.register_agent("reviewer", ReviewerAgent("rev1", "reviewer"))
    
    # We trigger the ping pong
    result = orchestrator.dispatch_goal("max_turns_trigger", max_turns=5)
    
    assert result.success is False
    assert result.reason == "Turn exhaustion"
    assert result.turns_used == 5

def test_cycle_detection():
    orchestrator = SupervisorOrchestrator()
    orchestrator.register_agent("researcher", ResearcherAgent("res1", "researcher"))
    orchestrator.register_agent("coder", CoderAgent("cod1", "coder"))
    orchestrator.register_agent("reviewer", ReviewerAgent("rev1", "reviewer"))
    
    result = orchestrator.dispatch_goal("cycle_trigger")
    
    assert result.success is False
    assert result.reason == "Cycle detected"

def test_blackboard_state_consistency():
    orchestrator = SupervisorOrchestrator()
    orchestrator.register_agent("researcher", ResearcherAgent("res1", "researcher"))
    orchestrator.register_agent("coder", CoderAgent("cod1", "coder"))
    orchestrator.register_agent("reviewer", ReviewerAgent("rev1", "reviewer"))
    
    result = orchestrator.dispatch_goal("Build a model")
    
    assert result.success is True
    assert "research_data" in orchestrator.state.blackboard
    assert "code" in orchestrator.state.blackboard
    assert "review" in orchestrator.state.blackboard
    assert orchestrator.state.blackboard['review'] == "Approved"
