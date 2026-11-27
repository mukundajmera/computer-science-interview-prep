# Bot Detection Platform — Common Pitfalls

1. Treating bot detection as static binary classification.
2. Omitting novelty/anomaly detection lane.
3. Hard-suspending on score only, ignoring confidence.
4. No explicit false-positive cost model.
5. Missing reason codes and policy versioning.
6. No investigator queue prioritization.
7. No campaign-level metrics for adaptation.
8. Blocking sensitive user actions on synchronous investigator review or heavy offline models, which breaches the sub-200 ms online risk-gate latency target. Keep inline scoring focused on fast supervised and anomaly branches backed by precomputed account snapshots, and feed investigator outcomes asynchronously into model updates.
9. Deploying policy threshold or model changes globally without traffic-slice canaries and automated rollback triggers. A miscalibrated rule across 500M DAU can suspend legitimate high-activity accounts rapidly, so canary policy updates on traffic slices and roll back when false-positive guardrails breach.
10. Evaluating actions in isolation without maintaining an `AccountRiskTimeline` or correlating coordinated campaigns across devices and IPs. Attackers evade single-request checks by spreading low-volume actions across accounts, so combine historical snapshots, remediation logs, and botnet graph signals.
