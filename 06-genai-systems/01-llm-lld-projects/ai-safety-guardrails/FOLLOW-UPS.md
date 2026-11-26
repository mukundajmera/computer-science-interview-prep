# AI Safety Guardrails - Follow-Up Questions

## Mandatory Interview Baseline
1. How would you handle a scenario where a PII redactor removes a word that structurally breaks the LLM's understanding of the prompt?
2. How could you parallelize the post-execution guardrails (like toxicity and hallucination checks) to reduce overall latency?
3. How do you deal with the "jailbreak" problem where users encode their prompt injection in Base64 or another language to bypass your heuristic detector?

## Optional Staff Follow-ups
1. How would you support streaming responses from the LLM provider? At what point do you evaluate toxicity if the text arrives token by token?
2. How would you track and monitor the rejection rate of specific guardrails to identify false positives?

## Variants and extensions
1. **Asynchronous Engine (v2):** Refactoring the pipeline to use async/await for parallel execution of non-mutating guardrails.
2. **Semantic Similarity Checks (v3):** Upgrading the Hallucination stub to actually compare embeddings of the generated text against the source context using a vector database.
3. **Tenant-Specific Policies:** Allowing different tenants to enable/disable specific guardrails or provide custom PII regex patterns.
4. **Streaming Guardrails:** Implementing a token buffer that evaluates chunks of generated text on the fly, cancelling the generation stream immediately if toxic content is detected.

## Interviewer probes to prepare
- "Why use a Pipeline or Chain of Responsibility here instead of a simple orchestrator function?"
- "What is the time complexity of running N heuristic guardrails over a prompt of length M? How does this scale?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach details](./APPROACH.md)
- [Design details](./DESIGN.md)
