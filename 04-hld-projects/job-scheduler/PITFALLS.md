# Job Scheduler — Common Pitfalls

1. Treating cron dispatch and dependency orchestration as the same scheduling model.
2. No lease/heartbeat ownership, which causes duplicate execution during worker failures.
3. Unlimited retries without capped backoff or dead-letter routing.
4. Storing mutable run state only in memory, preventing safe recovery after restart.
5. Ignoring clock skew/timezone handling for user-defined schedules.
6. Missing per-tenant quotas, allowing noisy tenants to starve queues.

## How to avoid them
- Define execution invariants first: who owns a run, when ownership expires, and when retry is allowed.
- Separate scheduler state from execution logs so replay and audit are possible.
- Use deterministic retry policies and idempotent job handlers.
