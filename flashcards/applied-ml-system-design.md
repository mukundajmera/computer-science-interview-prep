# Applied ML System Design Flashcards

40 question-only flashcards for applied-ML interview preparation.

---

## Framing and Objectives (10 Cards)

### Card 1
Front: What is the minimum framing triad before proposing an ML architecture?

Back: In ML system design, minimum is essential for bridging the gap between model training and production inference. It directly impacts both the scalability and the predictive accuracy of the system.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'minimum', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 2
Front: How do you distinguish business objective, product metric, and ML metric in one answer?

Back: You implement this by setting up rigorous offline evaluation metrics that tightly correlate with online business KPIs. Then, deploy using techniques like shadow testing or canary releases to monitor performance safely.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'distinguish', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 3
Front: Why is “maximize accuracy” usually a weak system-design objective?

Back: This is necessary because ML models degrade over time due to concept drift and data drift. Without this, the system risks serving stale or inaccurate predictions that harm the user experience.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding '“maximize', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 4
Front: What sentence format best states a precision guardrail?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails. Guardrails (like heuristics or rule-based filters) prevent catastrophic failures when the model encounters out-of-distribution inputs.

Back: Guardrails and fallback mechanisms (like heuristics or simpler models) are essential to prevent catastrophic failures when the primary ML model encounters out-of-distribution data.

### Card 5
Front: Which failure costs should you identify before model selection?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'costs', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 6
Front: How do you decide if a recommendation objective is short-term or long-term optimized?

Back: You implement this by setting up rigorous offline evaluation metrics that tightly correlate with online business KPIs. Then, deploy using techniques like shadow testing or canary releases to monitor performance safely.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'optimized', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 7
Front: What is a strong objective statement for bot detection?

Back: In ML system design, strong is essential for bridging the gap between model training and production inference. It directly impacts both the scalability and the predictive accuracy of the system.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'detection', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 8
Front: What makes a moderation objective robust against false positives?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'moderation', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 9
Front: How should you declare out-of-scope boundaries without weakening your answer?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'declare', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 10
Front: What is a strong 45-second ML-system-design wrap-up?

Back: In ML system design, strong is essential for bridging the gap between model training and production inference. It directly impacts both the scalability and the predictive accuracy of the system.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'ml-system-design', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

## Data, Labels, and Features (10 Cards)

### Card 11
Front: What is the fastest way to test for label scarcity risk in a design discussion?

Back: In ML system design, fastest is essential for bridging the gap between model training and production inference. It directly impacts both the scalability and the predictive accuracy of the system.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'fastest', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 12
Front: When should active labeling outperform random sampling?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'should', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 13
Front: What signal pattern suggests data leakage from offline to online?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: Aligning offline and online metrics ensures that improvements seen during model training translate to actual business value when deployed in production.

### Card 14
Front: How do you explain class imbalance impact on evaluation in one sentence?

Back: You implement this by setting up rigorous offline evaluation metrics that tightly correlate with online business KPIs. Then, deploy using techniques like shadow testing or canary releases to monitor performance safely.

Back: Evaluation must go beyond simple accuracy. Consider metrics like precision, recall, AUC, and business-specific KPIs to ensure the model aligns with product goals.

### Card 15
Front: Why should label sources be weighted differently in adversarial systems?

Back: This is necessary because ML models degrade over time due to concept drift and data drift. Without this, the system risks serving stale or inaccurate predictions that harm the user experience.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'should', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 16
Front: What is the minimum cold-start plan for recommendation systems?

Back: In ML system design, minimum is essential for bridging the gap between model training and production inference. It directly impacts both the scalability and the predictive accuracy of the system.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'minimum', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 17
Front: Which feature freshness failures most often break online relevance?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails. Feature stores are typically used to guarantee consistency between training and serving, minimizing training-serving skew.

Back: Feature engineering choices impact both model performance and inference latency. Online systems require fast feature retrieval, often using feature stores to guarantee low latency.

### Card 18
Front: How do you separate policy rules from model outputs cleanly?

Back: You implement this by setting up rigorous offline evaluation metrics that tightly correlate with online business KPIs. Then, deploy using techniques like shadow testing or canary releases to monitor performance safely.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'model', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 19
Front: What is the benefit of keeping policy version with each decision event?

Back: In ML system design, benefit is essential for bridging the gap between model training and production inference. It directly impacts both the scalability and the predictive accuracy of the system.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'benefit', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 20
Front: Which data slices should be mandatory in cohort diagnostics?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'mandatory', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

## Evaluation and Operations (10 Cards)

### Card 21
Front: What is the standard three-layer evaluation stack for applied ML systems?

Back: In ML system design, standard is essential for bridging the gap between model training and production inference. It directly impacts both the scalability and the predictive accuracy of the system.

Back: Evaluation must go beyond simple accuracy. Consider metrics like precision, recall, AUC, and business-specific KPIs to ensure the model aligns with product goals.

### Card 22
Front: Why are PR-oriented metrics often better than accuracy for rare harmful classes?

Back: This is necessary because ML models degrade over time due to concept drift and data drift. Without this, the system risks serving stale or inaccurate predictions that harm the user experience.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'often', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 23
Front: What does a safe canary rollout look like for an ML policy change?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'rollout', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 24
Front: Which metrics should trigger immediate rollback versus investigation-only alerts?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'rollback', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 25
Front: How do you explain delayed-outcome bias in recommendation evaluation?

Back: You implement this by setting up rigorous offline evaluation metrics that tightly correlate with online business KPIs. Then, deploy using techniques like shadow testing or canary releases to monitor performance safely.

Back: Evaluation must go beyond simple accuracy. Consider metrics like precision, recall, AUC, and business-specific KPIs to ensure the model aligns with product goals.

### Card 26
Front: What is the minimum dashboard set for moderation quality control?

Back: In ML system design, minimum is essential for bridging the gap between model training and production inference. It directly impacts both the scalability and the predictive accuracy of the system.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'quality', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 27
Front: How should review-queue saturation change policy actions?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'actions', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 28
Front: What incident signals differentiate drift from infrastructure failure?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'failure', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 29
Front: Why is decision lineage essential for post-mortems?

Back: This is necessary because ML models degrade over time due to concept drift and data drift. Without this, the system risks serving stale or inaccurate predictions that harm the user experience.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'decision', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 30
Front: What is the strongest argument for combining online and offline evaluation?

Back: In ML system design, strongest is essential for bridging the gap between model training and production inference. It directly impacts both the scalability and the predictive accuracy of the system.

Back: Aligning offline and online metrics ensures that improvements seen during model training translate to actual business value when deployed in production.

---

## Trade-offs and Follow-Ups (10 Cards)

### Card 31
Front: Why is layered detection (rules + ML + anomaly) stronger than a single-model stack?

Back: This is necessary because ML models degrade over time due to concept drift and data drift. Without this, the system risks serving stale or inaccurate predictions that harm the user experience.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'detection', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 32
Front: How do you justify exploration budget without harming user trust?

Back: You implement this by setting up rigorous offline evaluation metrics that tightly correlate with online business KPIs. Then, deploy using techniques like shadow testing or canary releases to monitor performance safely.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'trust', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 33
Front: Which trade-off framing best explains precision versus recall in moderation?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'trade-off', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 34
Front: How do you explain model lock-in risk to an interviewer quickly?

Back: You implement this by setting up rigorous offline evaluation metrics that tightly correlate with online business KPIs. Then, deploy using techniques like shadow testing or canary releases to monitor performance safely.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'lock-in', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 35
Front: What fallback do you choose when feature pipelines are stale?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails. Feature stores are typically used to guarantee consistency between training and serving, minimizing training-serving skew.

Back: Feature engineering choices impact both model performance and inference latency. Online systems require fast feature retrieval, often using feature stores to guarantee low latency.

### Card 36
Front: What should happen first when online quality drops after release?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'quality', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 37
Front: How do you choose between immediate hard enforcement and graduated policy?

Back: You implement this by setting up rigorous offline evaluation metrics that tightly correlate with online business KPIs. Then, deploy using techniques like shadow testing or canary releases to monitor performance safely.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'graduated', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 38
Front: What does “objective mismatch” look like in production metrics?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding '“objective', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 39
Front: How do you identify and communicate feedback-loop risk in ranking systems?

Back: You implement this by setting up rigorous offline evaluation metrics that tightly correlate with online business KPIs. Then, deploy using techniques like shadow testing or canary releases to monitor performance safely.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'communicate', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 40
Front: Which follow-up proves staff-level operational judgment in applied ML design?

Back: The design must balance the computational cost of feature extraction against the latency requirements of the online serving layer. Always consider fallback mechanisms for when the primary model fails.

Back: In applied ML systems, it's critical to balance model accuracy with system latency, cost, and maintainability across the entire lifecycle from training to deployment. Specifically, regarding 'applied', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.
