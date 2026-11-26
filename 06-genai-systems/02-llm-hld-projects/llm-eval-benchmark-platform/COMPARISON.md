# Comparison: Evaluation Strategies

## 1. Metric Methodologies

| Strategy | Pros | Cons | Use Case |
| :--- | :--- | :--- | :--- |
| **Traditional NLP (ROUGE/BLEU)** | Extremely fast, zero cost, deterministic. | Ignores semantic meaning; penalizes valid paraphrasing. | Exact match tasks, simple extraction. |
| **LLM-as-a-Judge (Zero-Shot)** | High correlation with human judgment, adaptable. | Expensive, slow, susceptible to prompt biases. | General Q&A, summarizing, RAG triad. |
| **LLM-as-a-Judge (Few-Shot/Chain-of-Thought)** | Highest accuracy, provides rationale for scores. | Very high token consumption, higher latency. | Critical offline CI/CD gating, complex reasoning tasks. |
| **Trained Classifiers (e.g., BERT models)** | Fast, relatively cheap, focused. | Narrow scope (e.g., only detects toxicity, not general quality); requires training data. | Online traffic sampling for specific safety guardrails. |

## 2. Benchmarking Frameworks

| Approach | Pros | Cons | When to choose |
| :--- | :--- | :--- | :--- |
| **Static Golden Sets (e.g., MMLU)** | Standardized, easy to compare across industry. | Models suffer from data contamination (they trained on the test set). | Baseline industry comparisons. |
| **Synthetic Dynamic Sets (Evol-Instruct)** | Prevents overfitting, scales infinitely. | Requires compute to generate; synthetic data may contain hallucinations. | Continuous red-teaming and robust regression testing. |
| **ELO Tournament (A/B testing)** | Reflects relative performance dynamically over time. | Requires continuous evaluation compute; A/B comparisons can be noisy. | Monitoring production model drift and comparing candidate models. |
