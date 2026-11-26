# Problem: Online Code Judge

## 1. Description
Design an Online Code Judge system (like LeetCode or HackerRank) that evaluates user-submitted source code against a set of test cases.

**Crucially, this system must only implement a trusted fake execution-adapter simulation.** Do not execute user-supplied code, shell commands, compilers or arbitrary files on the host. 

The system needs to accept code submissions in various programming languages, pass them to a fake adapter, and return a simulated verdict such as Accepted (AC), Wrong Answer (WA), Time Limit Exceeded (TLE), Memory Limit Exceeded (MLE), or Compilation Error (CE).

## 2. Requirements

### Core Requirements
1. **Language Support**: The judge must support multiple programming languages via fake adapters.
2. **Submission Queue**: Submissions should be processed asynchronously using a queue.
3. **Execution Simulation**: Each execution must be simulated. Stdlib timeouts/resource labels are not a security sandbox.
4. **External Sandbox Boundary**: A separately approved external VM/container boundary with filesystem/network/CPU/memory/output/process controls must be documented for production use (not implemented here).
5. **Verdicts**: The system must generate fake adapter-reported simulated verdicts based on deterministic fixture inputs:
   - AC: Accepted
   - WA: Wrong Answer
   - TLE: Time Limit Exceeded
   - MLE: Memory Limit Exceeded
   - CE: Compilation/Syntax Error

### System Constraints & Non-Functional Requirements
1. **Thread-Safety**: The submission queue and judge engine must be thread-safe to handle concurrent submissions.
2. **Extensibility**: It should be easy to add support for new fake programming languages.
3. **Immutability of Verdicts**: Trusted fake executor results drive pending/running/terminal verdicts once. Duplicate callbacks, cancellation, and timeout generations cannot replace a final verdict.

## 3. Example Use Case

```python
judge = CodeJudge()
judge.add_problem(
    problem_id="p1", 
    test_cases=[TestCase(input="2 3", expected="5")], 
    time_limit_ms=1000, 
    memory_limit_kb=65536
)

submission = Submission(
    user_id="u1",
    problem_id="p1",
    language="PYTHON",
    code="a, b = map(int, input().split()); print(a + b)"
)
judge.submit(submission)
verdict = judge.get_verdict(submission.id)
```
