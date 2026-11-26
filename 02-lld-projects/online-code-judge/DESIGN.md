# Design: Online Code Judge

## 1. Class Diagram

```mermaid
classDiagram
    class CodeJudge {
        -Map problems
        -Map submissions
        -SubmissionQueue queue
        -List workers
        +submit(Submission)
        +getVerdict(submissionId) Verdict
        +addProblem(Problem)
    }

    class Submission {
        -String id
        -String userId
        -String problemId
        -String code
        -Language language
        -Verdict verdict
        +updateVerdict(Verdict) boolean
    }

    class Problem {
        -String id
        -List~TestCase~ testCases
        -int timeLimitMs
        -int memoryLimitKb
    }

    class TestCase {
        -String input
        -String expectedOutput
    }
    
    class Verdict {
        <<enumeration>>
        PENDING
        RUNNING
        AC
        WA
        TLE
        MLE
        CE
    }

    class LanguageAdapter {
        <<interface>>
        +execute(code, input, timeLimit, memoryLimit) ExecutionResult
    }
    
    class FakePythonAdapter {
        +execute(code, input, timeLimit, memoryLimit) ExecutionResult
    }

    class FakeJavaAdapter {
        +execute(code, input, timeLimit, memoryLimit) ExecutionResult
    }
    
    CodeJudge o-- Submission
    CodeJudge o-- Problem
    Submission --> Verdict
    Problem o-- TestCase
    LanguageAdapter <|-- FakePythonAdapter
    LanguageAdapter <|-- FakeJavaAdapter
```

## 2. Component Design
- **CodeJudge**: The main facade class interacting with the client. Stores problems, submissions, and routes to a thread-safe queue.
- **LanguageAdapter**: A simulated execution interface. `FakePythonAdapter` and `FakeJavaAdapter` deterministically map known test strings to verdicts (AC, WA, TLE, MLE, CE).
- **Worker/Dispatcher**: Continuously polls the queue, fetches problem constraints, invokes `LanguageAdapter.execute`, and securely sets the terminal verdict exactly once, rejecting duplicate or delayed updates.
