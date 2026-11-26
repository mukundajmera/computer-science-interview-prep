# Applied ML System Design Quiz - Answers

> **Answer key for the Applied ML System Design Quiz with technical explanations.**

---

### Question 1
1. **D** - Clarify business objective and operating constraints

**Explanation:**
In a senior-level machine learning system design interview, diving straight into modeling is a major anti-pattern. The first step is always to clarify the business objective (what value the system brings to users or the company) and operating constraints (latency, throughput, cost, fairness). This ensures that the technical design is aligned with real-world requirements and avoids over-engineering a solution for the wrong problem.

*   **A is incorrect** because defining a loss function requires first knowing the objective we are optimizing.
*   **B is incorrect** because picking a model architecture before understanding the constraints and objectives leads to suboptimal or irrelevant designs.
*   **C is incorrect** because feature engineering should be guided by the business goal and the data available, which must be clarified first.

### Question 2
2. **B** - Minimize harmful exposure with precision guardrails

**Explanation:**
For content moderation, the primary goal is protecting users (minimizing harmful exposure). However, blindly maximizing content removal leads to high false positives, frustrating legitimate users and hurting the platform. Therefore, the strongest objective explicitly pairs minimizing harm with strict precision guardrails to bound the collateral damage.

*   **A is incorrect** because maximizing removed posts creates a perverse incentive to remove harmless content (high false positive rate).
*   **C is incorrect** because minimizing inference cost is an operational constraint, not the primary business objective of moderation.
*   **D is incorrect** because accuracy is a symmetric metric that does not distinguish between the asymmetric costs of false positives (censorship) and false negatives (harmful exposure).

### Question 3
3. **D** - CTR ignores long-term satisfaction and retention

**Explanation:**
Click-Through Rate (CTR) is a short-term proxy metric. Optimizing solely for CTR often leads to clickbait, sensationalism, or irrelevant content that tricks users into clicking. While CTR might spike initially, this degrades user trust and long-term satisfaction, ultimately hurting retention and the platform's overall health.

*   **A is incorrect** because CTR can definitely be A/B tested and is in fact one of the easiest metrics to test.
*   **B is incorrect** because while CTR can be noisy, its fundamental flaw is the misalignment with long-term user value, not just noise.
*   **C is incorrect** because CTR is mathematically trivial to compute online (clicks / impressions).

### Question 4
4. **D** - Business objective, ML objective, and failure costs

**Explanation:**
A staff-level engineer framing a problem must bridge the gap between business strategy and technical execution. This involves explicitly mapping the business objective to a tractable ML objective (e.g., surrogate loss functions) and, crucially, analyzing the costs of failure (false positives vs. false negatives) to guide architectural trade-offs.

*   **A is incorrect** because API contracts are system interfaces, which come after understanding the core objectives.
*   **B is incorrect** because library choices (like PyTorch vs TensorFlow) are implementation details that don't address the fundamental design problem.
*   **C is incorrect** because the data schema is an implementation detail, not the high-level problem framing.

### Question 5
5. **B** - Business metric -> product metric -> ML metric

**Explanation:**
A robust measurement hierarchy traces the ultimate goal down to what the model optimizes. The **business metric** (e.g., revenue, user retention) is the north star. The **product metric** (e.g., time spent on platform, successful purchases) is an actionable proxy for the business metric. Finally, the **ML metric** (e.g., LogLoss, NDCG) is what the model mathematically optimizes during training.

*   **A is incorrect** because it places ML metrics at the top, but ML metrics only exist to serve product and business goals.
*   **C is incorrect** because model metrics should be derived from product metrics, not infra metrics.
*   **D is incorrect** because infra metrics (like latency) are constraints, not the primary objective hierarchy driving model quality.

### Question 6
6. **C** - Control collateral damage from false positives

**Explanation:**
In asymmetric risk scenarios (like fraud detection, moderation, or banning users), a false positive means punishing a legitimate user. A precision guardrail is a strict operational threshold (e.g., "Precision must be >= 99%") designed specifically to cap this collateral damage, ensuring the model is only deployed or taking automated action when highly confident.

*   **A is incorrect** because guardrails often necessitate human review for low-confidence predictions, rather than replacing it.
*   **B is incorrect** because precision guardrails typically decrease recall, they do not increase it at all costs.
*   **D is incorrect** because guardrails are applied during evaluation and deployment, they do not reduce the actual model training time.

### Question 7
7. **B** - They hurt legitimate users and trust

**Explanation:**
In bot detection (or anti-abuse systems generally), a false positive means a legitimate, rule-abiding user is flagged, shadowbanned, or entirely blocked. This degrades user experience, generates support tickets, and destroys trust in the platform, which is often much more damaging long-term than letting a few bots slip through.

*   **A is incorrect** because removing all recall is the opposite of the problem; false positives occur when we try to push recall too high.
*   **C is incorrect** because false positives are evaluation outcomes, they do not inherently increase the model's file size.
*   **D is incorrect** because false positives do not affect GPU utilization.

### Question 8
8. **B** - Minimize abuse impact under bounded false-positive rate

**Explanation:**
This statement perfectly captures the dual nature of anti-abuse ML systems. The goal is to minimize the negative impact of bad actors, but this optimization must be strictly constrained by a bounded false-positive rate to protect legitimate users. It represents a mature, production-ready framing of the objective.

*   **A is incorrect** because detecting "all bots" (100% recall) is practically impossible and would require a 100% false-positive rate.
*   **C is incorrect** because maximizing bans per day incentivizes punishing innocent users to hit quotas.
*   **D is incorrect** because maximizing classifier confidence does not inherently align with business impact; the model could be confidently wrong.

### Question 9
9. **B** - Active labeling on uncertain/high-impact samples

**Explanation:**
When high-quality human labels are scarce and expensive, you cannot afford to label data randomly. Active learning strategies prioritize labeling the examples that will provide the most information to the model—typically those where the current model is highly uncertain, or samples that lie near the decision boundary in high-impact regions.

*   **A is incorrect** because ignoring labels and acting randomly destroys model performance and user experience.
*   **C is incorrect** because relying solely on synthetic data often leads to models that fail to generalize to real-world domain distributions.
*   **D is incorrect** because disabling online evaluation hides the problem; it does not solve the label scarcity issue.

### Question 10
10. **C** - Unrealistically high offline score not reproducible online

**Explanation:**
Data leakage occurs when information from the future (or the target label itself) accidentally leaks into the training features. In offline evaluation, this results in an artificially inflated, "too good to be true" performance metric. However, because this future information is unavailable at serving time, the online performance dramatically collapses.

*   **A is incorrect** because high inference latency is an infrastructure issue, completely independent of the model's predictive validity.
*   **B is incorrect** because low training variance simply means the model's predictions are consistent, which is unrelated to leakage.
*   **D is incorrect** because a validation score lower than training score is a sign of overfitting, not necessarily data leakage.

### Question 11
11. **B** - PR-oriented metrics and class-specific thresholds

**Explanation:**
When dealing with rare but highly sensitive classes (e.g., hate speech, severe policy violations), global metrics like accuracy are useless due to class imbalance. Instead, you need Precision-Recall (PR) oriented metrics (like PR-AUC) and must tune class-specific thresholds to manage the specific trade-offs and risks associated with each rare harm type.

*   **A is incorrect** because accuracy is heavily skewed by the majority class and will silently mask total failure on rare classes.
*   **C is incorrect** because throughput is an operational constraint, not an evaluation focus for model quality on rare classes.
*   **D is incorrect** because memory footprint is unrelated to how well the model detects harmful content.

### Question 12
12. **C** - Context + popularity priors + exploration budget

**Explanation:**
When a new user or item enters a recommendation system (cold-start), there is no historical behavioral data. The best strategy is to leverage available context (device, location, time), apply popularity priors (show what is generally liked), and explicitly allocate an exploration budget to show the cold items to a fraction of users to gather initial engagement data.

*   **A is incorrect** because full personalization is impossible without historical data for the user/item.
*   **B is incorrect** because randomly ranking permanently provides a terrible user experience and destroys engagement.
*   **D is incorrect** because showing no ranking (or a blank page) until a profile matures guarantees the profile will never mature because the user will leave.

### Question 13
13. **D** - Independent threshold/action control and safer rollouts

**Explanation:**
Decoupling the ML scoring service from the business policy engine allows product managers and safety teams to adjust action thresholds (e.g., "ban users if score > 0.95") dynamically without redeploying the model. It also enables complex multi-model rules and safer, staged rollouts of new model versions by adjusting policies.

*   **A is incorrect** because removing monitoring is a terrible practice; decoupling actually requires *more* specialized monitoring.
*   **B is incorrect** because language migration is a secondary infra benefit, not the primary systemic reason for the architecture.
*   **C is incorrect** because decoupling does not inherently speed up model training; it affects serving and operations.

### Question 14
14. **A** - Decision relevance and calibration stability

**Explanation:**
Feature freshness (how recently the feature values were updated) directly dictates how well the model can respond to changing user context or real-world events. Stale features lead to irrelevant decisions (e.g., recommending a product the user just bought) and cause the model's calibrated probabilities to drift as the data distribution shifts away from the training baseline.

*   **B is incorrect** because feature freshness impacts runtime data quality, not the underlying code style.
*   **C is incorrect** because feature freshness does not affect the number of API endpoints in the system architecture.
*   **D is incorrect** because build times are determined by CI/CD infrastructure, not the freshness of the data pipeline.

### Question 15
15. **D** - Not all labels have equal trust/quality

**Explanation:**
In adversarial environments (like fraud or abuse), bad actors actively try to poison data or evade detection. Labels come from various sources: user reports (noisy, easily manipulated), automated heuristics, and internal expert reviewers (high trust). Weighting label sources based on their trustworthiness is essential to prevent attackers from poisoning the training set.

*   **A is incorrect** because label weighting improves training quality; it is unrelated to model probability calibration.
*   **B is incorrect** because queueing is a system throughput issue, not a model label quality issue.
*   **C is incorrect** because label weighting is a mathematical operation during loss calculation, it does not improve compiler speed.

### Question 16
16. **D** - Offline gates + online monitoring + human audit slice

**Explanation:**
A production-grade evaluation stack requires defense in depth. Offline evaluation acts as a strict gate to catch catastrophic regressions before deployment. Online monitoring (A/B testing, shadow mode) measures true business impact. Finally, a continuous human audit slice (random sampling of decisions) provides ground truth to detect silent conceptual drift that automated metrics miss.

*   **A is incorrect** because offline evaluation cannot perfectly simulate real-world user behavior and domain shifts.
*   **B is incorrect** because unit tests only verify code correctness, they do not validate the statistical quality of the ML model.
*   **C is incorrect** because online-only evaluation risks exposing users to terrible, un-gated models, causing immediate harm.

### Question 17
17. **C** - position-sensitive quality and delayed outcomes

**Explanation:**
In ranking (like search or feeds), the position of an item drastically impacts user interaction (position bias). Evaluating ranking requires position-aware metrics like NDCG. Furthermore, outcomes in ranking are often delayed (a user clicks, but the actual purchase happens days later), making attribution and continuous evaluation highly complex compared to simple classification.

*   **A is incorrect** because SQL schema normalization is a database design issue, unrelated to ranking model quality.
*   **B is incorrect** because code style consistency has no bearing on the statistical quality of ranking algorithms.
*   **D is incorrect** because object storage tiering is an infrastructure concern, not a ranking evaluation concern.

### Question 18
18. **D** - Segment diagnostics and rollback if guardrails breach

**Explanation:**
When online quality degrades, the first operational priority is mitigating harm. If key guardrails (e.g., error rate, severe latency, catastrophic precision drop) are breached, you must immediately rollback to the previous stable version. Simultaneously, you must perform segmented diagnostics to isolate the failure to specific subpopulations, features, or platforms before attempting a fix.

*   **A is incorrect** because increasing model size is a long-term architectural change, not an incident response strategy.
*   **B is incorrect** because disabling all alerts removes your visibility into the problem and exacerbates the failure.
*   **C is incorrect** because retraining blindly without understanding the root cause of the drop often reinforces the bad data causing the issue.

### Question 19
19. **A** - limiting blast radius while validating behavior

**Explanation:**
A canary rollout routes a very small percentage of live traffic to the new model version while the vast majority remains on the stable version. The primary purpose is to validate that the new model integrates correctly with production infrastructure and doesn't crash or exhibit catastrophic behavioral regressions, effectively limiting the "blast radius" if something is wrong.

*   **B is incorrect** because replacing A/B tests is not the goal; canaries are for safety, A/B tests are for statistical significance of business metrics.
*   **C is incorrect** because canary rollouts have no impact on the cost of manual data annotation.
*   **D is incorrect** because canary rollouts do not reduce the number of features in the model.

### Question 20
20. **D** - investigate calibration/labeling before major rewrite

**Explanation:**
If statistical metrics (like LogLoss or AUC) drift significantly but product metrics (like revenue or click-through rate) remain stable, the model is likely still ranking correctly but its raw probabilities are miscalibrated, or the baseline distribution of the features has shifted. You should investigate calibration layers or recent label definitions before undertaking a costly model rewrite.

*   **A is incorrect** because removing monitoring blinds you to future, potentially harmful drift.
*   **B is incorrect** because if product impact is zero, there is no immediate production outage.
*   **C is incorrect** because metric drift proves the model is not perfect; its underlying statistical assumptions have shifted.

### Question 21
21. **D** - For auditability, rollback, and post-mortem attribution

**Explanation:**
In a complex applied ML system, decisions (like banning a user or denying a loan) must be defensible. Storing the exact model version, feature payload, and policy rules alongside the decision ensures complete auditability. If an incident occurs, this attribution is crucial for post-mortems and for correctly routing data during a rollback or retraining phase.

*   **A is incorrect** because prettier dashboards are a side effect, not the primary engineering or compliance reason.
*   **B is incorrect** because storing extra metadata actually increases storage costs and potentially I/O latency, it does not reduce p95 latency.
*   **C is incorrect** because storing metadata does not avoid the need to eventually retrain the model.

### Question 22
22. **D** - threshold breach with stability window and context

**Explanation:**
Production ML metrics are inherently noisy due to natural variance in user traffic. A robust alert triggers only when a metric breaches a threshold *and sustains that breach* over a defined stability window (e.g., 15 minutes). It must also include contextual data (e.g., "Precision dropped by 5% on iOS devices") to be actionable for on-call engineers.

*   **A is incorrect** because random sampling alone does not constitute an alerting mechanism.
*   **B is incorrect** because a weekly average is too slow; an incident could run for days before triggering the alert.
*   **C is incorrect** because alerting on a single noisy point causes alert fatigue, leading engineers to ignore actual emergencies.

### Question 23
23. **A** - priority policy + fallback action bands

**Explanation:**
In human-in-the-loop systems, the review queue has limited capacity. When it saturates (e.g., during an attack), the system must degrade gracefully. This requires a priority policy (routing the highest-risk/highest-confidence items to humans first) and fallback action bands (automatically taking conservative actions, like temporary holds, on lower-priority items instead of dropping them).

*   **B is incorrect** because disabling scoring completely breaks the system and provides no automated defense.
*   **C is incorrect** because silently dropping cases means malicious activity goes entirely unchecked.
*   **D is incorrect** because a full system shutdown causes a massive self-inflicted denial of service.

### Question 24
24. **A** - It improves resilience across known and novel attacks

**Explanation:**
A layered architecture provides defense in depth. Fast, deterministic rules catch known, obvious attacks cheaply. The ML model generalizes to catch complex patterns and variations. Anomaly detection catches entirely novel, zero-day attacks that neither rules nor supervised models have seen. Together, they provide superior resilience compared to any single method.

*   **B is incorrect** because layered architectures are chosen for technical efficacy, not just because they are trendy.
*   **C is incorrect** because supervised ML models still absolutely require large amounts of high-quality labeled data.
*   **D is incorrect** because layered detection certainly does not guarantee zero false positives.

### Question 25
25. **A** - prevent model lock-in and discover better candidates

**Explanation:**
Recommendation models suffer from a feedback loop where they only learn about items they choose to show. Over time, the model becomes overly confident in a narrow set of items (lock-in). An exploration budget deliberately allocates a small fraction of traffic to show new, uncertain, or historically ignored items, allowing the system to discover better candidates and continually update its understanding.

*   **B is incorrect** because exploration budgets do not remove personalization; they enhance it long-term by discovering new user interests.
*   **C is incorrect** because exploration budgets typically require *more* complex infrastructure, they do not inherently increase latency as a primary goal.
*   **D is incorrect** because avoiding metrics is nonsensical; exploration explicitly gathers metrics for new items.

### Question 26
26. **B** - better features/data and threshold calibration

**Explanation:**
In a precision-constrained environment (e.g., precision must be > 95%), you cannot simply lower the decision threshold to get more recall, as that will violate the precision guardrail. Therefore, the only mathematical way to improve recall while maintaining fixed precision is to improve the fundamental discriminative power of the model, which requires better features, cleaner data, or a more capable architecture.

*   **A is incorrect** because blindly reducing model capacity will hurt both precision and recall.
*   **C is incorrect** because disabling human review affects operational throughput, not the intrinsic recall of the ML model.
*   **D is incorrect** because dropping guardrails violates the premise of the question (precision is fixed by policy).

### Question 27
27. **B** - jumping to model choice before objective and constraints

**Explanation:**
The most common and fatal mistake in an ML system design interview is acting like a Kaggle competitor instead of an engineer. Immediately proposing "Transformers" or "XGBoost" without first defining the business goal, the scale of the data, latency requirements, and the cost of errors demonstrates a profound lack of senior-level engineering maturity.

*   **A is incorrect** because asking clarifying questions is highly encouraged and necessary to define the problem scope.
*   **C is incorrect** because discussing trade-offs is a requirement for passing the interview, not an anti-pattern.
*   **D is incorrect** because drawing a data flow is a critical step in the architectural design phase.

### Question 28
28. **A** - chosen operating point, risks, and next validation step

**Explanation:**
A strong wrap-up summarizes the entire system. It explicitly states the chosen operating point (e.g., "We will deploy at a 0.85 threshold to guarantee 99% precision"), acknowledges the remaining systemic risks (e.g., "We are vulnerable to coordinated botnets"), and defines the immediate next step to validate the design (e.g., "We will launch a shadow mode test to monitor false positives").

*   **B is incorrect** because an API summary alone misses the ML-specific operational and risk context.
*   **C is incorrect** because a data model summary alone is incomplete for an applied ML design.
*   **D is incorrect** because listing framework names (e.g., "I used PyTorch and Kafka") provides zero insight into the strategic design of the system.

### Question 29
29. **C** - User behavior can bias future training data and ranking decisions

**Explanation:**
In applied ML, the predictions made by the model today dictate the data collected tomorrow. If a model ranks an item #1, it gets more clicks purely due to position bias. If this data is fed back into training without debiasing, the model learns that its past predictions were "correct," leading to runaway echo chambers and degraded performance.

*   **A is incorrect** because adding more compute cannot mathematically fix a fundamental statistical bias in the training distribution.
*   **B is incorrect** because feedback loops fundamentally alter data distributions, they do not merely affect caching infrastructure.
*   **D is incorrect** because feedback loops are one of the most critical and challenging problems in production ML.

### Question 30
30. **A** - confidence-banded actions with human escalation

**Explanation:**
When moderation errors carry severe real-world consequences (e.g., legal liability, catastrophic PR, deep user harm), fully automated black-box enforcement is too risky. The standard production strategy utilizes confidence bands: low scores are ignored, extremely high scores trigger automated action, and intermediate (uncertain) scores are systematically escalated to human review teams.

*   **B is incorrect** because maximizing automation indiscriminately leads to unacceptable rates of high-stakes false positives.
*   **C is incorrect** because random enforcement is illegal in many jurisdictions, deeply unethical, and ruins user trust.
*   **D is incorrect** because waiting for perfect certainty means the model will never act, reducing recall to zero and allowing all harm through.
