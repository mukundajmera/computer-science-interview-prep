# Bot Detection — Common Interview Pitfalls

## 1. Designing for static attackers
Ignoring adversarial evolution leads to rapid model obsolescence.

## 2. No graduated enforcement
Binary ban/no-ban policy creates excessive collateral damage.

## 3. Over-reliance on one model
Single-model stacks are brittle to concept drift.

## 4. No investigator label strategy
Scarce high-quality labels must be allocated deliberately.

## 5. No appeal workflow
False positives without clear recovery path erode trust.

## 6. Missing feature-pipeline fallback
Detection gaps appear during stream lag or feature outages.

---

## Quick Self-Check

- Did I model adversarial drift and adaptation cadence?
- Did I include multi-stage enforcement actions?
- Did I include investigator + appeal feedback loops?
- Did I define fallback behavior when features are stale?
