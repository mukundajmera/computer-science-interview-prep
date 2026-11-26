# Follow-Up Questions

1.  **How do you handle a scenario where the Judge LLM API is completely down during a critical CI deployment?**
    *   *Good Answer:* Graceful degradation. Fall back to smaller, self-hosted open-source judges (e.g., Llama-3-70B-Instruct) for critical gating. Alternatively, pause the CI pipeline or allow manual overrides by authorized personnel.

2.  **How do you evaluate the Evaluator?**
    *   *Good Answer:* We maintain a "meta-evaluation" dataset—a highly curated, human-annotated set of examples where we know the absolute ground truth. We periodically run our LLM-as-a-Judge against this meta-dataset and measure its correlation with human labels (e.g., Pearson/Spearman correlation).

3.  **Your platform samples 5% of production traffic. Users are complaining about data privacy. How do you address this?**
    *   *Good Answer:* Implement a strict PII scrubbing layer (using fast NER models like Presidio) *before* the data is logged to Kafka. Furthermore, allow tenants/users to opt-out of data collection, dynamically adjusting the sampling rules.

4.  **The synthetic data generator is creating test cases that are impossible for any model to answer. How do you detect and filter these?**
    *   *Good Answer:* Before adding synthetic cases to the Golden Registry, run a verification pass. Ask a strong model to answer the new question. If it fails, or if it indicates the question is malformed/unanswerable, discard the synthetic test case.

5.  **How do you prevent the judge from favoring longer, albeit lower-quality, answers? (Verbosity Bias)**
    *   *Good Answer:* Explicitly instruct the judge in the prompt to penalize unnecessary verbosity. Alternatively, enforce strict length constraints on the target models, or use a length-normalized scoring function post-evaluation.
