# Content Moderation — Common Interview Pitfalls

## 1. No explicit operating threshold
Ignoring precision guardrails leads to unworkable enforcement policy.

## 2. Treating class imbalance as minor
Rare harmful events require targeted sampling and calibration strategy.

## 3. Missing policy/action layer
A score alone is not a production decision.

## 4. No human review capacity model
Review queues can become the bottleneck.

## 5. No feedback loop
Without reports/appeals/moderator labels, performance decays quickly.

## 6. Conflating this with full LLM governance platform
Interview scope drifts away from applied moderation architecture.

---

## Quick Self-Check

- Did I define business objective + precision guardrail?
- Did I include policy actions beyond binary score?
- Did I model review queue saturation and fallback behavior?
- Did I cover drift/evasion and recalibration cadence?
