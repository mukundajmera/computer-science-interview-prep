# Bot Detection Platform — Approach

## 45-Minute Flow

| Phase | Time | Expected Outcome |
|---|---|---|
| Framing | 6 min | adversarial objective + FP guardrails |
| Estimates | 5 min | event scale + label scarcity |
| API + model | 8 min | risk-action contract |
| Architecture | 12 min | dual-path scoring and orchestration |
| Deep dives | 10 min | remediation ladder + adaptation loop |
| Wrap-up | 4 min | trade-offs + first 10x bottleneck |

## Recommended Sequence

1. Define success as reduced abuse impact under controlled collateral damage.
2. Separate online gate checks from deeper offline analysis.
3. Merge supervised and anomaly outputs through calibrated policy.
4. Explicitly model investigator queue prioritization.
5. Close with campaign adaptation and rollback triggers.
