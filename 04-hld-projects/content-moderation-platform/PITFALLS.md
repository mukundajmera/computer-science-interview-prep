# Content Moderation Platform — Common Pitfalls

1. Treating moderation as only model accuracy, not policy risk.
2. Using one binary action instead of a staged action ladder.
3. Ignoring reviewer throughput and queue overload.
4. No policy/model version tracking in decisions.
5. Missing rollback strategy for threshold updates.
6. Coupling heavy enforcement work directly in the post path.
7. No metric plan for disagreement and drift.
8. Failing to calibrate separate score and confidence thresholds per policy category, applying the same cutoff to reversible demotions and irreversible removals. Require higher confidence for `remove` than `demote` and route near-threshold items to the human review lane to preserve precision guardrails.
9. Leaving the synchronous moderation gateway without a defined timeout or degraded-mode policy when the Inference Service or async enforcement lane fails. Keep the Moderation Gateway as state owner, route timed-out items to retry or human review per policy, and let async enforcement reconcile from last known state without blocking posts.
10. Using FIFO reviewer queues without exposure-based prioritization or backpressure controls during 3x traffic peaks (~35K eval/s). Prioritize review tasks by expected exposure and severity with strict SLA classes, and tighten auto-demote thresholds temporarily when reviewer queues saturate.
