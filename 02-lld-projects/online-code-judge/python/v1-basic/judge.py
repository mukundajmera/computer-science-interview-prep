
from typing import List, Dict, Optional

class Verdict:
    PENDING = "PENDING"
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
        if self.verdict != Verdict.PENDING:
            return False
        self.verdict = verdict
        return True

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
        problem = self.problems.get(submission.problem_id)
        if not problem:
            submission.update_verdict(Verdict.CE)
            return

        # Synchronous execution
        for tc in problem.test_cases:
            if "TLE" in submission.code:
                submission.update_verdict(Verdict.TLE)
                return
            if "MLE" in submission.code:
                submission.update_verdict(Verdict.MLE)
                return
            if "RE" in submission.code:
                submission.update_verdict(Verdict.RE)
                return
            if "WA" in submission.code:
                submission.update_verdict(Verdict.WA)
                return
        
        submission.update_verdict(Verdict.AC)
