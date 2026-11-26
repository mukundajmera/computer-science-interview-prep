
# Social Post Search System - System Comparison

| Concern | This System | Closest Existing System | Key Difference |
|---|---|---|---|
| Core shape | Domain-specific workflow | Generic service patterns | Domain invariants drive consistency choices |
| Read strategy | Cache + derived model | Cache-first HLD baseline | Stronger domain-specific filtering/ranking |
| Write strategy | Idempotent mutation + events | Standard CRUD + async | Higher correctness pressure on critical path |

## Reuse guidance

- Reuse message-queue and cache patterns from existing HLD concepts.
- Keep domain-specific invariants documented separately from infra choices.
