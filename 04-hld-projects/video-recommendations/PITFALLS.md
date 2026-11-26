# Video Recommendations — Common Interview Pitfalls

## 1. Treating recommendation as full-catalog online scoring
This is computationally infeasible at platform scale.

## 2. Optimizing CTR only
Leads to clickbait and poor long-term user satisfaction.

## 3. Ignoring exploration
No exploration causes model lock-in and stale recommendations.

## 4. Missing feedback-loop bias discussion
User interactions are both signal and intervention, creating evaluation bias.

## 5. No cold-start strategy
New users/videos need explicit fallback pathways.

## 6. Mixing streaming-delivery concerns into recommendation design
Scope drift hides ranking-system trade-offs.

---

## Quick Self-Check

- Did I design a multi-stage pipeline?
- Did I define objective beyond CTR?
- Did I cover cold start and exploration?
- Did I address delayed metrics and feedback-loop bias?
