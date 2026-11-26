from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import queue
import threading

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
        self._verdict = Verdict.PENDING
        self._lock = threading.Lock()
    
    def update_verdict(self, verdict: str) -> bool:
        with self._lock:
            if self._verdict not in (Verdict.PENDING, Verdict.RUNNING):
                return False
            self._verdict = verdict
            return True
            
    def get_verdict(self) -> str:
        with self._lock:
            return self._verdict

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

class FakeRunner(LanguageRunner):
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

class RunnerFactory:
    @staticmethod
    def get_runner(language: str) -> LanguageRunner:
        return FakeRunner()

class Worker(threading.Thread):
    def __init__(self, judge_engine):
        super().__init__()
        self.judge = judge_engine
        self.daemon = False
        self.running = True

    def run(self):
        while self.running or not self.judge.submission_queue.empty():
            try:
                submission = self.judge.submission_queue.get(timeout=0.1)
                self.judge._process(submission)
                self.judge.submission_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                pass

class OnlineCodeJudge:
    def __init__(self, num_workers=2):
        self.problems: Dict[str, Problem] = {}
        self.submissions: Dict[str, Submission] = {}
        self.submission_queue = queue.Queue()
        self.workers = []
        self._lock = threading.Lock()
        
        for _ in range(num_workers):
            w = Worker(self)
            w.start()
            self.workers.append(w)

    def add_problem(self, problem: Problem):
        with self._lock:
            self.problems[problem.problem_id] = problem

    def submit(self, submission: Submission):
        with self._lock:
            self.submissions[submission.submission_id] = submission
        self.submission_queue.put(submission)

    def get_verdict(self, submission_id: str) -> Optional[str]:
        with self._lock:
            sub = self.submissions.get(submission_id)
        return sub.get_verdict() if sub else None

    def _process(self, submission: Submission):
        if not submission.update_verdict(Verdict.RUNNING):
            return

        with self._lock:
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
        
    def stop(self):
        for w in self.workers:
            w.running = False
        for w in self.workers:
            w.join(timeout=2.0)
