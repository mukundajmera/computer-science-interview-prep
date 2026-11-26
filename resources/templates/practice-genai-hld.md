# 🎯 GenAI HLD Interview Practice Template

> **Type:** Generative AI System Design  
> **Total Time:** 45 minutes  
> **Flagship Example:** Document Q&A (RAG) System

---

## ⏱️ Time-Boxed Structure

| Phase | Duration | Focus |
|-------|----------|-------|
| 1. Clarify Use Case & LLM Role | 5 min | What does the LLM do? Input/output modalities, user expectations |
| 2. Token Budget & Cost Estimation | 5 min | Token counts, cost per query, latency waterfall, throughput targets |
| 3. Architecture Sketch | 10 min | End-to-end system: retrieval, prompt assembly, LLM call, response |
| 4. LLM Pipeline Deep Dive | 10 min | Chunking, embedding, retrieval, ranking, prompt construction, generation |
| 5. Safety & Guardrails | 5 min | Input filtering, output validation, PII handling, hallucination mitigation |
| 6. Evaluation & Observability | 5 min | Offline metrics, online monitoring, A/B testing, feedback loops |
| 7. Wrap-Up | 5 min | Trade-offs summary, follow-up discussion |

---

## 📊 Scoring Rubric

| Dimension | 1 — Weak | 2 — Below Avg | 3 — Meets Bar | 4 — Strong | 5 — Exceptional |
|-----------|----------|---------------|---------------|------------|-----------------|
| **Use Case Clarity** | Doesn't clarify LLM role | Vague understanding of what LLM does | Clear LLM role, input/output defined | Distinguishes LLM tasks from classic backend, scopes well | Identifies when NOT to use an LLM, proposes hybrid approach |
| **Cost & Latency Awareness** | No mention of tokens or cost | Acknowledges cost exists | Estimates token counts and cost per query | Models latency waterfall, identifies bottlenecks | Optimizes token budget, proposes caching/batching strategies |
| **Architecture Design** | No clear architecture | Missing key components (e.g., retrieval) | Core pipeline present: retrieve → augment → generate | Clean separation of concerns, async where needed | Handles multi-model routing, streaming, fallbacks |
| **LLM Pipeline Depth** | Treats LLM as black box | Basic prompt-in, text-out understanding | Discusses chunking, embedding, retrieval, prompt design | Covers ranking, context window management, few-shot strategies | Proposes advanced techniques: HyDE, re-ranking, chain-of-thought |
| **Safety & Guardrails** | Not mentioned | Brief mention of safety | Input/output filtering discussed | PII handling, hallucination mitigation, content policies | Red-teaming strategy, compliance (EU AI Act), layered defense |
| **Evaluation Plan** | No evaluation discussed | Mentions "we should test it" | Defines 2-3 offline metrics (faithfulness, relevance) | Online + offline eval, A/B testing, human-in-the-loop | Continuous eval pipeline, regression detection, feedback loops |
| **Trade-Offs** | No trade-offs | Acknowledges trade-offs | Discusses 1-2 (cost vs quality, latency vs accuracy) | Structured analysis connecting to business requirements | Quantitative trade-off reasoning with concrete thresholds |

**Scoring:** 24+ = Strong Hire · 19-23 = Hire · 14-18 = Lean Hire · <14 = No Hire

---

## ✅ Self-Review Checklist

After completing your practice session, verify:

### Use Case & Scope
- [ ] Clarified what the LLM is responsible for vs traditional backend
- [ ] Defined input/output formats and user expectations
- [ ] Identified whether retrieval-augmented generation (RAG) is needed
- [ ] Scoped what is out of bounds for this design

### Cost & Performance
- [ ] Estimated average tokens per request (input + output)
- [ ] Calculated cost per query and monthly cost at target scale
- [ ] Mapped the latency waterfall (retrieval + LLM inference + post-processing)
- [ ] Discussed caching strategies for repeated or similar queries

### Architecture
- [ ] Drew end-to-end architecture diagram
- [ ] Included ingestion pipeline (chunking, embedding, indexing)
- [ ] Included query pipeline (retrieval, ranking, prompt assembly, generation)
- [ ] Addressed streaming responses to the user

### LLM Pipeline
- [ ] Discussed chunking strategy and chunk size trade-offs
- [ ] Covered embedding model selection
- [ ] Explained retrieval mechanism (vector search, hybrid search)
- [ ] Designed prompt template with system instructions + context + query

### Safety
- [ ] Input filtering for prompt injection and jailbreak attempts
- [ ] Output validation for hallucinations and harmful content
- [ ] PII detection and redaction strategy
- [ ] Content policy enforcement

### Evaluation
- [ ] Defined offline metrics (faithfulness, relevance, groundedness)
- [ ] Planned online monitoring (latency, error rates, user satisfaction)
- [ ] Discussed A/B testing approach for model/prompt changes
- [ ] Considered human feedback collection mechanism

---

## 🔗 Related Resources

- [GenAI Design Template](../../06-genai-systems/02-llm-hld-projects/GENAI-DESIGN-TEMPLATE.md) — Full design template
- [GenAI Systems](../../06-genai-systems/) — Concepts, LLD components, and HLD projects
- [GenAI SD Framework](../../06-genai-systems/GENAI-SD-FRAMEWORK.md) — How to answer any GenAI SD question

---

*Use this rubric to grade yourself honestly after each practice session. Focus on dimensions where you score below 3.*
