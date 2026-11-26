
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

class Verdict:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    AC = "AC"
    WA = "WA"
    TLE = "TLE"
    MLE = "MLE"
    CE = "CE"
    RE = "RE"

class TestCase:
    def __init__(self, input_str: str, expected_output: str):
        self.input_str = input_str
        self.expected_output = expected_output

class Problem:
    def __init__(self, problem_id: str, test_cases: List[TestCase], time_limit_ms: int, memory_limit_kb: int):
        self.problem_id = problem_id
        self.test_cases = test_cases
        self.time_limit_ms = time_limit_ms
        self.memory_limit_kb = memory_limit_kb

class Submission:
    def __init__(self, submission_id: str, user_id: str, problem_id: str, language: str, code: str):
        self.submission_id = submission_id
        self.user_id = user_id
        self.problem_id = problem_id
        self.language = language
        self.code = code
        self.verdict = Verdict.PENDING
    
    def update_verdict(self, verdict: str) -> bool:
        if self.verdict not in (Verdict.PENDING, Verdict.RUNNING):
            return False
        self.verdict = verdict
        return True

class ExecutionResult:
    def __init__(self, output: str, time_taken_ms: int, memory_used_kb: int, error: bool = False):
        self.output = output
        self.time_taken_ms = time_taken_ms
        self.memory_used_kb = memory_used_kb
        self.error = error

class LanguageRunner(ABC):
    """
    Trusted fake execution-adapter simulation.
    
    SECURITY NOTICE:
    Do not execute user-supplied code, shell commands, compilers, or arbitrary files on the host.
    stdlib timeouts/resource labels are not a security sandbox.
    Actual execution must occur in a separately approved VM/container boundary 
    with strict filesystem, network, CPU, memory, output, and process controls.
    MLE/TLE are adapter-reported simulations, not unproven isolation.
    """

    @abstractmethod
    def execute(self, code: str, input_str: str) -> ExecutionResult:
        pass

class PythonRunner(LanguageRunner):
    def execute(self, code: str, input_str: str) -> ExecutionResult:
        if "TLE" in code:
            return ExecutionResult("", 2000, 1000)
        if "MLE" in code:
            return ExecutionResult("", 100, 1000000)
        if "RE" in code:
            return ExecutionResult("", 10, 10, True)
        if "WA" in code:
            return ExecutionResult("wrong", 10, 10)
        return ExecutionResult(input_str, 10, 10)

class JavaRunner(LanguageRunner):
    def execute(self, code: str, input_str: str) -> ExecutionResult:
        return PythonRunner().execute(code, input_str)

class RunnerFactory:
    @staticmethod
    def get_runner(language: str) -> LanguageRunner:
        if language == "PYTHON":
            return PythonRunner()
        elif language == "JAVA":
            return JavaRunner()
        return PythonRunner()

class CodeJudge:
    def __init__(self):
        self.problems: Dict[str, Problem] = {}
        self.submissions: Dict[str, Submission] = {}

    def add_problem(self, problem: Problem):
        self.problems[problem.problem_id] = problem

    def submit(self, submission: Submission):
        self.submissions[submission.submission_id] = submission
        self._process(submission)

    def get_verdict(self, submission_id: str) -> Optional[str]:
        sub = self.submissions.get(submission_id)
        return sub.verdict if sub else None

    def _process(self, submission: Submission):
        if not submission.update_verdict(Verdict.RUNNING):
            return

        problem = self.problems.get(submission.problem_id)
        if not problem:
            submission.update_verdict(Verdict.CE)
            return

        runner = RunnerFactory.get_runner(submission.language)

        for tc in problem.test_cases:
            res = runner.execute(submission.code, tc.input_str)
            if res.error:
                submission.update_verdict(Verdict.RE)
                return
            if res.time_taken_ms > problem.time_limit_ms:
                submission.update_verdict(Verdict.TLE)
                return
            if res.memory_used_kb > problem.memory_limit_kb:
                submission.update_verdict(Verdict.MLE)
                return
            if res.output != tc.expected_output:
                submission.update_verdict(Verdict.WA)
                return
        
        submission.update_verdict(Verdict.AC)
