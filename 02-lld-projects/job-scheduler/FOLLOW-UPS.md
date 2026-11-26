# Job Scheduler - Follow-Ups

## Follow-up questions
1. How would you introduce DAG dependencies without rewriting the run-state model?
2. How should queue admission behave when worker capacity is saturated?
3. How would you enforce tenant-level fairness with bounded workers?
4. How would you add exactly-once side-effect boundaries when handlers call external systems?
5. How would you recover leases or checkpoints after a process crash?

## Variants and extensions
1. Priority + deadline scheduling mix.
2. Workflow-level retries vs task-level retries.
3. Per-tenant quota pools and admission control.
4. Pluggable persistence for run checkpoints and dead-letter records.

## Interviewer probes to prepare
- "What is your backpressure strategy when workers saturate?"
- "How do you prevent duplicate execution after crash recovery?"
- "What metrics prove scheduler health?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
