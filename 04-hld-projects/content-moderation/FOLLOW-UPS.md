# Content Moderation — Follow-Up Questions

## 1. How do we support policy differences by geography?
Add policy versioning by jurisdiction with audit-friendly decision traces.

## 2. How do we prioritize reviewer queues?
Use risk-weighted prioritization based on exposure and confidence band.

## 3. How do we handle coordinated evasion attacks?
Introduce adversarial detection, campaign-level correlation, and rapid threshold overrides.

## 4. How do we reduce false-positive appeal load?
Add high-precision override model and staged demotion before deletion for ambiguous classes.

## 5. How do we rollback a bad model release?
Use shadow/canary evaluation and policy-gated rollout switches.

## 6. How do we extend to video/audio?
Split extraction pipeline and apply modality-specific models with shared policy layer.
