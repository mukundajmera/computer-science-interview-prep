# Evaluation Rubric: LLM Eval Platform

## 1. Core Architecture (30%)
*   **[L4 - Beginner] Asynchronous Execution:** Did the candidate design a robust, queue-based worker system to handle offline and online evaluation tasks as an intuitive minimum example?
*   **[L5 - Core] Scalability & Fault Tolerance:** Is the system resilient to third-party API rate limits and transient failures, demonstrating operational trade-offs?

## 2. GenAI Evaluation Deep Dive (40%)
*   **[L4 - Beginner] Evaluation Validity:** Did the candidate use self-consistency voting or chain-of-thought prompting for the judge to ensure evaluation validity?
*   **[L5 - Core] Judge Uncertainty:** Did the candidate explicitly mention and mitigate LLM judge biases (position bias, verbosity bias) to address judge uncertainty trade-offs?
*   **[L5 - Core] RAG Triad:** Did the candidate separate evaluation into Faithfulness, Answer Relevance, and Context Precision?
*   **[L5 - Core] Dynamic Testing:** Did they propose a mechanism to prevent test stagnation (e.g., synthetic data generation via Evol-Instruct)?

## 3. Continuous Benchmarking & Security (15%)
*   **[L5 - Core] ELO System:** Did they describe an automated A/B tournament system to maintain relative model rankings over time?
*   **[L6/L7 - Staff] Leakage Safeguards:** Did the candidate design optional failure traces ensuring test set contamination leakage boundaries hold against model training pipelines?

## 4. Operational Trade-offs (15%)
*   **[L5 - Core] Cost Control:** Did they discuss strategies to minimize judge API costs (caching, model routing)?
*   **[L6/L7 - Staff] Privacy / Failure Trace:** Did they provide an optional failure trace with assumptions on PII scrubbing mechanisms before sending production logs to third-party judges?
