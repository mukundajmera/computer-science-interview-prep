# Job Scheduler — Interview Scoring Rubric

| Dimension | Weight | Strong signal |
|---|---|---|
| Requirement framing | 10% | Separates one-off, cron, and dependency-driven jobs; defines exactly-once vs at-least-once goal |
| Capacity + sizing | 15% | Converts jobs/min, fan-out, retry rate into queue and worker sizing |
| API/workflow design | 10% | Clean submit/cancel/pause/resume semantics with idempotency keys |
| Data model | 15% | Clear run history model, lease metadata, and retry/backoff state |
| Execution architecture | 20% | Distinguishes scheduler, dispatcher, worker pools, and dead-letter handling |
| Failure + recovery depth | 20% | Covers worker crash, lease expiry, duplicate execution, and replay safety |
| Communication quality | 10% | Trade-offs are explicit with clear fallback/degraded modes |

## Score bands (0-35)
- **30-35:** Strong hire; design handles correctness and operability.
- **22-29:** Hire; minor gaps in scaling or failure detail.
- **15-21:** Lean no-hire; architecture is plausible but brittle.
- **<15:** No-hire; core scheduling invariants are unclear.

## Related content
- [Workflow Orchestration Concept](../../03-hld-concepts/workflow-orchestration/THEORY.md)
- [Message Queues](../../03-hld-concepts/message-queues/THEORY.md)
- [LLD Job Scheduler](../../02-lld-projects/job-scheduler/)
