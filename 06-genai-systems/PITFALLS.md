# 🚨 GenAI System Design — Top Interview Pitfalls

> **GenAI system design interviews surface failure modes that simply don't exist in classical SD.** Token economics, hallucination handling, safety layers, and evaluation strategies are first-class concerns — yet candidates routinely skip them. This guide catalogues the 10 most common mistakes and gives you a concrete fix for each.

---

## 📑 Table of Contents

- [The Top 10 Pitfalls](#the-top-10-pitfalls)
- [Quick Self-Check Checklist](#-quick-self-check-checklist)
- [Cross-Links](#-cross-links)

---

## The Top 10 Pitfalls

### 1. Ignoring Token Economics

❌ **The Mistake**: Treating LLM calls as free — no estimation of prompt/completion tokens, no mention of per-request cost, and no discussion of how costs scale with traffic.

🎯 **What Interviewers Expect**: A back-of-envelope calculation: *"Average prompt is ~800 tokens, completion ~400 tokens, at $X per 1K tokens → $Y per request → $Z/day at peak QPS."* Show you understand that LLM inference is orders of magnitude more expensive than a DB read.

💡 **Quick Fix**: Always include a **Token & Cost Estimation** step right after your functional requirements — treat it like the bandwidth estimation of classical SD.

---

### 2. Skipping Safety & Guardrails

❌ **The Mistake**: Designing a system with no input validation beyond auth, no output filtering, and zero discussion of prompt injection, PII leakage, or toxic content.

🎯 **What Interviewers Expect**: A dedicated safety layer in your architecture: input guardrails (prompt injection detection, PII scrubbing), output guardrails (toxicity filters, factuality checks), and a policy engine that can be updated without redeploying.

💡 **Quick Fix**: Draw a **Safety Filter** box on both the input and output paths of every LLM call — then explain what each one checks.

---

### 3. Over-Engineering Agents

❌ **The Mistake**: Reaching for multi-step agentic loops, tool calling, and planning modules when the problem is a straightforward retrieval + generation task.

🎯 **What Interviewers Expect**: You match complexity to the use case. A document Q&A system needs RAG, not an autonomous agent. Show you can distinguish *"retrieve-then-generate"* from *"plan-execute-reflect"* and justify which one fits.

💡 **Quick Fix**: Ask yourself — *"Does this task require multi-step reasoning or tool use?"* If not, start with simple RAG and only escalate to agents if the interviewer pushes.

---

### 4. No Evaluation Strategy

❌ **The Mistake**: Finishing the design with no explanation of how you'd know the system is working well — no metrics, no offline eval, no mention of human review.

🎯 **What Interviewers Expect**: A layered evaluation approach: automated metrics (BLEU/ROUGE for summarization, accuracy for classification), LLM-as-judge for open-ended quality, human evaluation for edge cases, and A/B testing for production changes.

💡 **Quick Fix**: End every GenAI design with a **"How do we measure quality?"** section covering offline eval, online metrics, and feedback loops.

---

### 5. Treating LLMs as Deterministic

❌ **The Mistake**: Assuming the same input always produces the same output, ignoring temperature settings, hallucination risk, and the need for output validation.

🎯 **What Interviewers Expect**: Explicit acknowledgement that LLMs are non-deterministic. Discuss temperature tuning, structured output enforcement (JSON mode, function calling), retry strategies, and fallback paths when the model produces garbage.

💡 **Quick Fix**: State upfront — *"LLM output is probabilistic"* — then show how your design handles the variance (validation, retries, fallbacks).

---

### 6. Ignoring Latency Waterfall

❌ **The Mistake**: Quoting a single latency number for the whole request without breaking down where time is actually spent.

🎯 **What Interviewers Expect**: A latency breakdown: retrieval (~50–200 ms), prompt assembly (~10 ms), time-to-first-token (~200–800 ms), token generation (~20–50 ms/token × N tokens), post-processing and safety checks (~50–100 ms). Show you understand TTFT vs total generation time and how streaming helps perceived latency.

💡 **Quick Fix**: Draw a **latency waterfall diagram** and call out which stages can be parallelized or streamed.

---

### 7. No Retrieval Quality Discussion

❌ **The Mistake**: Saying *"we use RAG"* without discussing how documents are chunked, what embedding model is used, whether a reranker is applied, or how retrieval quality is measured.

🎯 **What Interviewers Expect**: Specifics — chunking strategy (fixed-size vs semantic), overlap, metadata enrichment, embedding model choice, approximate nearest neighbor (ANN) index tuning, and a reranking step (cross-encoder or Cohere Rerank) to improve precision before the LLM sees the context.

💡 **Quick Fix**: Whenever you draw a RAG pipeline, annotate each stage: **Chunk → Embed → Index → Retrieve → Rerank → Generate**.

---

### 8. Missing the Caching Opportunity

❌ **The Mistake**: Not discussing any caching strategy despite LLM inference being the most expensive and slowest component in the system.

🎯 **What Interviewers Expect**: Multiple caching layers — exact-match prompt caching for repeated queries, semantic caching (embedding similarity) for near-duplicate queries, KV-cache reuse for multi-turn conversations, and provider-level prompt caching (e.g., Anthropic prompt caching) for shared system prompts.

💡 **Quick Fix**: Ask — *"Will users ask similar questions?"* If yes, add a **semantic cache** layer before the LLM call.

---

### 9. Not Discussing Model Selection

❌ **The Mistake**: Defaulting to *"we'll use GPT-4"* without considering cost, latency, or task-fit trade-offs — or mentioning model routing for different request types.

🎯 **What Interviewers Expect**: A model selection rationale: small/fast models for classification and simple tasks, large models for complex reasoning, and a routing layer that directs requests to the appropriate model tier based on complexity, cost budget, or latency requirements.

💡 **Quick Fix**: Propose at least **two model tiers** (e.g., GPT-3.5/Haiku for simple tasks, GPT-4/Sonnet for complex ones) and explain the routing logic.

---

### 10. Forgetting the Human in the Loop

❌ **The Mistake**: Designing a fully autonomous system with no escalation path — assuming the LLM will handle 100% of cases correctly.

🎯 **What Interviewers Expect**: A confidence-based routing mechanism: high-confidence responses go directly to users, low-confidence responses are flagged for human review, and there's a feedback loop where human corrections improve the system over time.

💡 **Quick Fix**: Add a **confidence threshold** check after the LLM response — below the threshold, route to a human queue.

---

## ✅ Quick Self-Check Checklist

Before you finish your GenAI system design answer, verify you addressed:

- [ ] **Token economics** — Did I estimate tokens/request and cost/day?
- [ ] **Safety & guardrails** — Are there input AND output safety layers?
- [ ] **Appropriate complexity** — Is my architecture matched to the problem (RAG vs agents)?
- [ ] **Evaluation strategy** — Can I explain how to measure system quality?
- [ ] **Non-determinism** — Did I address hallucinations, retries, and output validation?
- [ ] **Latency breakdown** — Did I discuss TTFT, streaming, and the latency waterfall?
- [ ] **Retrieval quality** — If using RAG, did I discuss chunking, embeddings, and reranking?
- [ ] **Caching** — Did I mention semantic caching, KV-cache, or prompt caching?
- [ ] **Model selection** — Did I justify my model choice and consider routing?
- [ ] **Human-in-the-loop** — Is there a fallback path for low-confidence responses?

---

## 🔗 Cross-Links

| Resource | Why It Helps |
|----------|-------------|
| [GenAI SD Framework](./GENAI-SD-FRAMEWORK.md) | The 6-step framework that structures your answer — these pitfalls map to its steps |
| [Classic vs GenAI SD](./CLASSIC-VS-GENAI.md) | Understand what's fundamentally different so you don't miss GenAI-specific concerns |
| [GenAI Concepts](./00-concepts/) | Deep dives into RAG, safety, evaluation, and other building blocks |
| [GenAI HLD Projects](./02-llm-hld-projects/) | Full system designs that demonstrate pitfall-free approaches |
| [Classical HLD Concepts](../03-hld-concepts/) | Foundational distributed systems knowledge that still applies |

---

*Use this as a final review checklist before any GenAI system design interview. Avoiding these 10 pitfalls puts you ahead of the majority of candidates.*
