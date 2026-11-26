# Evaluation Harness - Follow-Up Questions

## Follow-up questions
1. How would you integrate LLM-as-a-judge for semantic evaluation alongside rule-based metrics?
2. How do you mitigate position bias and verbosity bias when using LLMs as judges?
3. How would you run evaluations in parallel across large benchmark suites of 100k+ examples?
4. How do you implement automated regression detection in a CI/CD pipeline?
5. How would you compute human-agreement correlation (e.g. Cohen's Kappa) for evaluation metrics?

## Variants and extensions
- Multi-turn conversation evaluation (evaluating dialog consistency across turns).
- Tool-calling evaluation (AST matching for function arguments and execution outputs).
- Cost, latency, and throughput benchmark harness.

## Interviewer probes to prepare
- "Why use the Strategy pattern for different evaluation metrics? How does this make testing easier?"
- "How do you handle rate limits and retries when calling external LLM APIs for evaluation?"
- "What is the memory overhead of storing all evaluation results in memory, and how would you optimize it for large datasets?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Design details](./DESIGN.md)
