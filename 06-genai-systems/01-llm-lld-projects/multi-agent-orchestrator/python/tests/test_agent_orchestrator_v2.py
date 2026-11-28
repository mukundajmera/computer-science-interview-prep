import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from agent_orchestrator_v2 import (
    SupervisorOrchestratorV2,
    ResearcherAgent,
    CoderAgent,
    ReviewerAgent,
    BaseAgent,
    AgentMessage,
    TransientAgentError,
    normalize_content,
)


def _standard_orchestrator(**kwargs):
    orchestrator = SupervisorOrchestratorV2(**kwargs)
    orchestrator.register_agent("researcher", ResearcherAgent("res1", "researcher"))
    orchestrator.register_agent("coder", CoderAgent("cod1", "coder"))
    orchestrator.register_agent("reviewer", ReviewerAgent("rev1", "reviewer"))
    return orchestrator


# ---- Parity: every v1 test re-run against the v2 module ----

def test_supervisor_worker_handoff():
    orchestrator = _standard_orchestrator()
    result = orchestrator.dispatch_goal("Build a web server")

    assert result.success is True
    assert result.reason == "Success"
    assert "Code approved" in result.final_result
    assert len(orchestrator.state.history) == 4


def test_max_turns_termination():
    orchestrator = _standard_orchestrator()
    result = orchestrator.dispatch_goal("max_turns_trigger", max_turns=5)

    assert result.success is False
    assert result.reason == "Turn exhaustion"
    assert result.turns_used == 5


def test_cycle_detection():
    orchestrator = _standard_orchestrator()
    result = orchestrator.dispatch_goal("cycle_trigger")

    assert result.success is False
    assert result.reason == "Cycle detected"


def test_blackboard_state_consistency():
    orchestrator = _standard_orchestrator()
    result = orchestrator.dispatch_goal("Build a model")

    assert result.success is True
    assert "research_data" in orchestrator.state.blackboard
    assert "code" in orchestrator.state.blackboard
    assert orchestrator.state.blackboard['review'] == "Approved"


# ---- v2 improvement 1: semantic cycle detection (PITFALLS #1) ----

class TimestampedCoder(CoderAgent):
    """Produces bad code with a fresh timestamp on every retry, so its
    replies never repeat exactly."""

    def __init__(self, name, role):
        super().__init__(name, role)
        self.attempts = 0

    def process(self, message, state):
        if "cycle_trigger" in message.content:
            self.attempts += 1
            code = f"bad_code generated at 2026-11-28T22:00:{self.attempts:02d}"
            state.blackboard['code'] = code
            return AgentMessage(
                sender=self.name,
                recipient="reviewer",
                role=self.role,
                content=code,
                step_index=message.step_index + 1
            )
        return super().process(message, state)


class RephrasingReviewer(ReviewerAgent):
    """Rejects bad code with a fresh timestamp each time, the exact
    decoration that blinds v1's exact-string cycle check."""

    def __init__(self, name, role):
        super().__init__(name, role)
        self.rejections = 0

    def process(self, message, state):
        if "bad_code" in state.blackboard.get('code', ''):
            self.rejections += 1
            return AgentMessage(
                sender=self.name,
                recipient="coder",
                role=self.role,
                content=f"cycle_trigger rejected at 2026-11-28T22:05:{self.rejections:02d}",
                step_index=message.step_index + 1
            )
        return super().process(message, state)


def test_semantic_cycle_detected_despite_rephrasing():
    orchestrator = _standard_orchestrator()
    orchestrator.register_agent("coder", TimestampedCoder("cod1", "coder"))
    orchestrator.register_agent("reviewer", RephrasingReviewer("rev1", "reviewer"))

    result = orchestrator.dispatch_goal("cycle_trigger", max_turns=10)

    assert result.success is False
    assert result.reason == "Cycle detected (semantic)"
    assert result.turns_used < 10  # halted early, not by turn exhaustion


def test_normalize_strips_timestamps_and_case():
    a = normalize_content("Rejected at 2026-11-28T22:00:01  PLEASE fix")
    b = normalize_content("rejected   at 2026-11-28T23:59:59 please fix")
    assert a == b


def test_normalize_keeps_counters_distinct():
    assert normalize_content("max_turns_trigger_1") != normalize_content("max_turns_trigger_2")


# ---- v2 improvement 2: per-agent retries ----

class FlakyResearcher(ResearcherAgent):
    def __init__(self, name, role, failures_before_success):
        super().__init__(name, role)
        self.failures_left = failures_before_success
        self.attempts = 0

    def process(self, message, state):
        self.attempts += 1
        if self.failures_left > 0:
            self.failures_left -= 1
            raise TransientAgentError("rate limited")
        return super().process(message, state)


def test_transient_failure_retried_and_run_succeeds():
    orchestrator = _standard_orchestrator(max_retries=2)
    flaky = FlakyResearcher("res1", "researcher", failures_before_success=2)
    orchestrator.register_agent("researcher", flaky)

    result = orchestrator.dispatch_goal("Build a web server")

    assert result.success is True
    assert result.retries_used == 2
    assert flaky.attempts == 3


def test_retry_exhaustion_fails_cleanly():
    orchestrator = _standard_orchestrator(max_retries=2)
    orchestrator.register_agent("researcher", FlakyResearcher("res1", "researcher", failures_before_success=99))

    result = orchestrator.dispatch_goal("Build a web server")

    assert result.success is False
    assert "retries" in result.reason
    assert result.retries_used == 2


# ---- v2 improvement 3: content budget (PITFALLS #3) ----

def test_budget_exhaustion_halts_run():
    orchestrator = _standard_orchestrator(max_budget_chars=20)
    result = orchestrator.dispatch_goal("Build a web server with a very long goal string")

    assert result.success is False
    assert result.reason == "Budget exhausted"


def test_run_within_budget_succeeds():
    orchestrator = _standard_orchestrator(max_budget_chars=100000)
    result = orchestrator.dispatch_goal("Build a web server")

    assert result.success is True
    assert result.reason == "Success"
