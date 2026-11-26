# Coach Answer: Coding Platform (LeetCode-like) - HLD

> Type: High-Level Design  
> Difficulty: Advanced  
> Time Target: 45 minutes

---

## Requirements And Constraints

### Functional Requirements

1. List coding problems with metadata and pagination.
2. Retrieve a single problem statement with language-specific starter code.
3. Accept code submissions and return execution verdicts.
4. Support contest leaderboard views with periodic refresh.

### Non-Functional Requirements

| Metric | Target |
|---|---|
| Submission response start | < 5s for initial status |
| Availability | 99.9% |
| Isolation | Untrusted code must be sandboxed |
| Throughput | Burst handling during contest windows |
| Consistency | Eventual consistency acceptable for leaderboard |

### Constraints

- User code is untrusted and may be malicious.
- Runtime and memory budgets are strict per submission.
- Contest traffic is highly spiky near start and end times.
- Fairness requires deterministic test execution and scoring rules.

### Out Of Scope

- Billing and payments.
- Full account profile system.
- Rich social features.

---

## API Sketch

```http
GET /api/v1/problems?page=1&limit=50
GET /api/v1/problems/{problemId}?language=python
POST /api/v1/problems/{problemId}/submissions
GET /api/v1/submissions/{submissionId}
GET /api/v1/leaderboards/{contestId}?page=1&limit=100
```

Example submission payload:

```json
{
  "language": "python",
  "sourceCode": "def solve(): pass",
  "clientSubmissionId": "d7345f9f-07b1-46cb-a1b1-20bc93f73d4b"
}
```

---

## Architecture

### Core Components

1. API Gateway: auth, rate limits, request routing.
2. Problem Service: problem catalog and statements.
3. Submission Service: accepts submissions and persists metadata.
4. Judge Orchestrator: dispatches to sandboxes and tracks execution status.
5. Sandbox Workers: isolated runtime execution.
6. Leaderboard Projection: aggregates accepted submissions into ranking views.
7. Data Stores:
- Relational store for problems, contests, and submissions metadata.
- Queue for asynchronous execution.
- Cache for hot leaderboard pages.

### Write Path (Submission)

1. Client posts submission.
2. Submission Service validates payload and stores `QUEUED` record.
3. Orchestrator enqueues execution request.
4. Sandbox worker executes test batches under resource limits.
5. Orchestrator stores final verdict and metrics.
6. Leaderboard projection updates contest ranking asynchronously.

### Read Path (Leaderboard)

1. Client fetches leaderboard page.
2. Service reads cached projection first.
3. Cache miss falls back to projection store.
4. Response includes pagination cursor and ranking snapshot timestamp.

---

## Scoring Rubric

| Dimension | Strong Signal |
|---|---|
| Requirements | Clarifies contest vs practice mode, fairness, and out-of-scope items quickly |
| Security | Explicit sandbox isolation and resource caps |
| Data Model | Separates submission metadata from execution artifacts |
| Architecture | Async execution queue + deterministic judging pipeline |
| Leaderboard | Eventual projection with clear staleness contract |
| Trade-offs | Discusses latency vs cost vs isolation strength |

---

## Common Pitfalls

1. Running user code directly in app servers.
2. Blocking request thread until all tests complete.
3. Building leaderboard from raw submissions on every request.
4. Missing idempotency key for duplicate submission retries.
5. Ignoring contest-end burst behavior and queue backpressure.

---

## Follow-Up Questions

1. How would you harden language isolation for multi-tenant contests?
2. How would you support partial scoring with hidden test sets?
3. How would you prevent plagiarism at platform scale?
4. How would you add rejudge flows when test data changes?
5. What changes for 10x peak contest traffic?

---

## Variants And Extensions

1. Practice mode with incremental hint unlocks.
2. Live contests with freeze windows and delayed official ranking.
3. Company-assessment mode with stricter audit logging.
4. Multi-region contest hosting with local judges and global projection merge.

---

## Cross-Links

- [API Gateway Concept](../../../03-hld-concepts/api-gateway/THEORY.md)
- [Caching Concept](../../../03-hld-concepts/caching/THEORY.md)
- [Message Queues Concept](../../../03-hld-concepts/message-queues/THEORY.md)
- [Rate Limiting LLD](../../../02-lld-projects/rate-limiter/PROBLEM.md)
