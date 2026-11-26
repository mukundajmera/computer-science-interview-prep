# Applied ML System Design Quiz

30 questions focused on applied-ML interview framing, objective design, evaluation rigor, drift handling, and adversarial adaptation.

Time: 40 minutes  
Difficulty: Medium-Hard

---

## Section 1: Framing and objectives (8)

### Question 1
What is the best first move in an applied ML design interview?

A) Define loss function and optimizer
B) Pick model architecture immediately
C) Start feature brainstorming
D) Clarify business objective and operating constraints

### Question 2
Which objective is strongest for content moderation?

A) Maximize removed posts
B) Minimize harmful exposure with precision guardrails
C) Minimize inference cost only
D) Maximize model accuracy

### Question 3
Why is “maximize CTR” often insufficient for recommendations?

A) CTR cannot be A/B tested
B) CTR is always noisy
C) CTR is hard to compute online
D) CTR ignores long-term satisfaction and retention

### Question 4
A staff-level framing usually includes:

A) Only API contracts
B) Library choices and package versions
C) Only data schema
D) Business objective, ML objective, and failure costs

### Question 5
Most robust objective hierarchy is:

A) Model metric -> infra metric -> business metric
B) Business metric -> product metric -> ML metric
C) Product metric -> infra metric -> ML metric
D) Infra metric -> product metric -> business metric

### Question 6
A precision guardrail is primarily used to:

A) Replace human review
B) Increase recall at any cost
C) Control collateral damage from false positives
D) Reduce model training time

### Question 7
In bot detection, false positives are dangerous because:

A) They remove all recall
B) They hurt legitimate users and trust
C) They increase model size
D) They lower GPU utilization

### Question 8
Best short objective statement for bot detection:

A) Detect all bots
B) Minimize abuse impact under bounded false-positive rate
C) Maximize bans per day
D) Maximize classifier confidence

## Section 2: Data, features, and labels (7)

### Question 9
When high-quality labels are scarce, first strategy should be:

A) Ignore labels and use random actions
B) Active labeling on uncertain/high-impact samples
C) Train only on synthetic data
D) Disable online evaluation

### Question 10
A strong signal of data leakage is:

A) High inference latency
B) Low training variance
C) Unrealistically high offline score not reproducible online
D) Validation score lower than training score

### Question 11
For rare harmful classes, useful evaluation focus is:

A) Accuracy only
B) PR-oriented metrics and class-specific thresholds
C) Throughput only
D) Memory footprint only

### Question 12
Cold-start handling in recommendations should prioritize:

A) Full personalization from first request
B) Random ranking permanently
C) Context + popularity priors + exploration budget
D) No ranking until profile matures

### Question 13
Why keep policy engine separate from model service?

A) Removes need for monitoring
B) Easier language migration
C) Faster model training
D) Independent threshold/action control and safer rollouts

### Question 14
Feature freshness mostly affects:

A) Decision relevance and calibration stability
B) Code style
C) Number of API endpoints
D) Build times

### Question 15
In adversarial systems, label source weighting matters because:

A) It replaces calibration
B) It prevents queueing
C) It improves compiler speed
D) Not all labels have equal trust/quality

## Section 3: Evaluation and operations (8)

### Question 16
Best evaluation stack:

A) Offline only
B) Unit tests only
C) Online only
D) Offline gates + online monitoring + human audit slice

### Question 17
For ranking systems, top concern beyond relevance is:

A) SQL schema normalization
B) code style consistency
C) position-sensitive quality and delayed outcomes
D) object storage tiering

### Question 18
When online quality drops after launch, first response is:

A) Increase model size
B) Disable all alerts
C) Retrain blindly
D) Segment diagnostics and rollback if guardrails breach

### Question 19
A canary rollout is primarily for:

A) limiting blast radius while validating behavior
B) replacing A/B tests
C) lowering annotation cost
D) reducing feature count

### Question 20
Metric drift without product impact usually implies:

A) remove monitoring
B) immediate production outage
C) model is perfect
D) investigate calibration/labeling before major rewrite

### Question 21
Why store policy/model version with decisions?

A) For prettier dashboards
B) To reduce p95 latency
C) To avoid retraining
D) For auditability, rollback, and post-mortem attribution

### Question 22
A robust alert should be based on:

A) random sampling only
B) weekly average only
C) single noisy point
D) threshold breach with stability window and context

### Question 23
Review-queue saturation should trigger:

A) priority policy + fallback action bands
B) disable scoring
C) silent dropping of cases
D) full system shutdown

## Section 4: Trade-offs and follow-ups (7)

### Question 24
Best explanation for layered detection (rules + model + anomaly):

A) It improves resilience across known and novel attacks
B) It is trendy
C) It removes need for labels
D) It guarantees zero false positives

### Question 25
Exploration budget in recommendations exists to:

A) prevent model lock-in and discover better candidates
B) remove personalization
C) increase latency
D) avoid metrics

### Question 26
If precision is fixed by policy, improving recall usually requires:

A) reducing model capacity blindly
B) better features/data and threshold calibration
C) disabling human review
D) dropping all guardrails

### Question 27
Most dangerous anti-pattern in applied ML interviews:

A) asking clarifying questions
B) jumping to model choice before objective and constraints
C) discussing trade-offs
D) drawing data flow

### Question 28
Best wrap-up for applied ML design includes:

A) chosen operating point, risks, and next validation step
B) only API summary
C) only data model summary
D) framework names used

### Question 29
A correct statement about feedback loops is:

A) They can be ignored with more compute
B) They only affect cache hit rate
C) User behavior can bias future training data and ranking decisions
D) They are irrelevant in production

### Question 30
For high-stakes moderation errors, preferred strategy is:

A) confidence-banded actions with human escalation
B) maximize automation only
C) random enforcement for fairness
D) no action until certainty is perfect

