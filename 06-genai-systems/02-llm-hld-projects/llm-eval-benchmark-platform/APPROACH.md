# Approach: LLM Evaluation & Benchmark Platform

## 1. Deconstruct the Problem

When asked to design an evaluation platform, realize that this is fundamentally a distributed task execution system optimized for GenAI workloads. 

Key pillars to address:
1.  **Data Management:** Where do golden datasets come from, and how do we prevent test stagnation (synthetic generation)?
2.  **Execution Engine:** How do we reliably execute thousands of async tasks against rate-limited third-party APIs (the judges)?
3.  **GenAI Specifics:** How do we trust the judge? You must discuss position bias, self-consistency, and RAG-specific metrics (the Triad).
4.  **Continuous Benchmarking:** How do we know if a model degrades over time? (ELO Tournament).

## 2. Guide the Interview

1.  **Start with the "Why":** Acknowledge that standard software tests (unit/integration) don't work for non-deterministic LLMs. We need probabilistic evaluation.
2.  **Define the Scope:** Clarify whether this includes inline guardrails (sync) or offline/async evaluation. Push for async offline CI/CD and online sampling to keep the design focused on evaluation rather than latency-critical serving.
3.  **Draw the Core Pipeline:** Show the flow from Test Data -> Task Queue -> Worker -> Judge Model -> Metrics DB.
4.  **Deep Dive into "Trusting the Judge":** This is where you score points. Explain that `LLM(Response A, Response B)` might output 'A' just because it saw it first.
    * Emphasize that position swaps and voting mitigate specific biases but do not prove correctness.
    * Detail how golden-set splits, contamination/tenant privacy, pair-order/random-seed controls and judge/human disagreement are formally defined.
    * Crucially, explicitly state limitations: LLM judges are probabilistic and do not mathematically prove correctness.
    * Quality gates state costs, uncertainty, abstention and human escalation.
5.  **Address Scale:** Highlight the cost and rate limits of using GPT-4 as a judge. Propose caching identical outputs and routing simpler tasks to smaller, self-hosted models.

## 3. Key Vocabulary to Use

*   **LLM-as-a-Judge:** Using a strong model to evaluate weak ones.
*   **Position Bias:** The tendency of LLMs to prefer the first option presented.
*   **Self-Consistency:** Running the same evaluation multiple times at T>0 and taking the majority vote.
*   **Evol-Instruct:** Systematically mutating simple prompts into complex ones to generate synthetic test data.
*   **RAG Triad:** Context Precision, Faithfulness, Answer Relevance.
*   **Red-Teaming:** Adversarial testing to find security flaws.
*   **ELO Rating:** A method for calculating relative skill levels (borrowed from chess) applied to models.
