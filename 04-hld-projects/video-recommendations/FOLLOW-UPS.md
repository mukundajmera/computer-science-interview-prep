# Video Recommendations — Follow-Up Questions

## 1. How do we personalize for anonymous users?
Use session-context ranking and popularity priors until identity signals mature.

## 2. How do we mitigate clickbait and low-retention content?
Add quality-adjusted objective and post-click retention penalties.

## 3. How do we support creator fairness?
Apply controlled diversification constraints and fairness metrics.

## 4. How do we detect recommender drift?
Track calibration, distribution shifts, and long-horizon KPI deltas.

## 5. How do we run safe model experiments?
Use offline gates plus online A/B canaries with rollback thresholds.

## 6. How do we support policy-aware ranking?
Inject safety/policy filters before final ranking and monitor suppression effects.
