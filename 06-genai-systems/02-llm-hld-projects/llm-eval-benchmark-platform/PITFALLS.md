# Common Pitfalls & Mistakes

1.  **Treating LLM-as-a-Judge as Infallible:**
    *   *Mistake:* Blindly trusting a single zero-shot response from a judge model.
    *   *Correction:* Acknowledge position bias and verbosity bias (LLMs prefer longer answers), and implement swapped-order evaluation and self-consistency voting to address judge uncertainty. Concrete counterexample: Returning simple metrics without variance boundaries or swap checks in the worker code.

2.  **Ignoring Rate Limits & Costs:**
    *   *Mistake:* Designing a system that hammers the OpenAI API with 10,000 concurrent evaluation requests during a CI run.
    *   *Correction:* Implement robust rate limiting, exponential backoff, circuit breakers on workers, and use semantic caching. Concrete counterexample: Implementing synchronous blocking calls `eval = await judge_api.evaluate(batch)` without retry or backoff wrappers.

3.  **Conflating Online Serving with Offline Eval:**
    *   *Mistake:* Putting the evaluation engine directly in the synchronous request path for user traffic.
    *   *Correction:* Ensure online monitoring uses asynchronous log tailing/sampling to avoid impacting user latency.

4.  **Static Test Data Overfitting & Leakage:**
    *   *Mistake:* Using a fixed set of 1,000 prompts for a year, or exposing eval datasets to the training pipeline.
    *   *Correction:* Implement synthetic data generation (Evol-Instruct) to continuously mutate and expand the test surface area. Concrete counterexample: Failing to isolate the test registry storage or implement leakage safeguards, meaning `model.train(datasets.load('all'))` accidentally ingests the eval set.

5.  **Forgetting RAG-Specific Nuances:**
    *   *Mistake:* Evaluating a RAG system as a single black box using only Q&A accuracy.
    *   *Correction:* Break it down using the RAG Triad. You must evaluate the retriever (did it find the right docs?) separately from the generator (did it stick to the docs?).
