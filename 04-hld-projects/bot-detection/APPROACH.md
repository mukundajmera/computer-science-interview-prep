# Design Approach for Bot Detection

## Interview flow (45 minutes)

| Phase | Time | Focus |
|---|---|---|
| Clarify problem | 6 min | account surfaces, remediation policy, FP budget |
| Estimation | 6 min | event rates, prevalence, investigator throughput |
| API + state model | 8 min | account risk state and action lifecycle |
| Architecture | 13 min | feature stream, risk engine, policy action path |
| Deep dives | 9 min | label strategy, anomaly detection, calibration |
| Wrap-up | 3 min | drift playbook and rollout safety |

## Suggested execution order

1. Set business objective and false-positive guardrails.
2. Define risk-state machine for accounts.
3. Build layered detection (rules + supervised + anomaly).
4. Add remediation policy and appeal/investigator feedback loop.
5. Close with adversarial drift and fail-safe operation.
