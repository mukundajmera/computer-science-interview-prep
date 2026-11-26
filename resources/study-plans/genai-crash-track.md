# 🤖 GenAI Crash Track (1–2 Weeks)

A focused plan for engineers who need to prepare for GenAI system design interviews quickly.

---

## 📋 Overview

| Day | Focus Area | Time | Topics |
|-----|------------|------|--------|
| 1 | GenAI Foundations | 4-5 hrs | LLM basics, RAG architecture, token budgets |
| 2 | RAG Deep Dive | 5-6 hrs | Retrieval patterns, vector DBs, embedding models |
| 3 | GenAI LLD Components | 5-6 hrs | Chunker, retriever, prompt builder |
| 4 | Safety & Evaluation | 4-5 hrs | Hallucination mitigation, toxicity filters, eval metrics |
| 5 | HLD: RAG-Based Search | 5-6 hrs | End-to-end enterprise search system |
| 6 | HLD: Conversational Chatbot | 5-6 hrs | Full chatbot architecture with memory |
| 7 | Mock Practice & Review | 4-5 hrs | Timed practice, cheatsheet review |
| 8–10 | Extended Practice (Optional) | 3-4 hrs/day | AI Copilot HLD, agentic workflows, weak areas |

**Total Time:** ~35–50 hours over 1–2 weeks

---

## 📅 Day 1: GenAI Foundations

**Goal:** Build mental model of LLM-powered system design.

### Morning Session (2-2.5 hrs)

- [ ] **LLM-Oriented System Design** (1.5 hrs)
  - 📁 Study: [06-genai-systems/00-concepts/llm-system-design/](../../06-genai-systems/00-concepts/llm-system-design/)
  - Topics:
    - How LLM inference differs from traditional request-response
    - Token budgets and latency implications
    - Model selection trade-offs (cost vs quality vs speed)
  - 💡 Key point: LLM calls are expensive and non-deterministic—design around that

- [ ] **RAG Architecture Overview** (45 min)
  - 📁 Study: [06-genai-systems/00-concepts/rag-architecture/](../../06-genai-systems/00-concepts/rag-architecture/)
  - Topics:
    - Retrieval-Augmented Generation end-to-end flow
    - Why RAG over fine-tuning for most interview scenarios
    - Core components: chunker → embedder → retriever → generator
  - 💡 Key point: RAG is the most commonly asked GenAI interview pattern

### Afternoon Session (2-2.5 hrs)

- [ ] **Prompting, Tools & Agents** (1 hr)
  - 📁 Study: [06-genai-systems/00-concepts/prompting-tools-agents/](../../06-genai-systems/00-concepts/prompting-tools-agents/)
  - Topics:
    - Prompt engineering basics (system prompts, few-shot, chain-of-thought)
    - Tool-using agents and function calling
    - When to use agents vs simple prompt chains

- [ ] **Token Budget Estimation Practice** (1 hr)
  - Practice calculating:
    - Input tokens (context window allocation)
    - Output tokens (response length)
    - Cost per request at scale
  - 📁 Reference: [GenAI System Design One-Pager](../cheatsheets/genai-system-design-one-pager.md)
  - 📁 Reference: [Token / Cost / Latency Planning](../../06-genai-systems/00-concepts/token-cost-latency/)

### Evening Review (30 min)

- [ ] Summarize in your own words: What is RAG and why is it preferred?
- [ ] List 3 trade-offs when choosing an LLM model for a system

---

## 📅 Day 2: RAG Deep Dive

**Goal:** Understand retrieval patterns and vector database internals.

### Morning Session (2.5-3 hrs)

- [ ] **RAG Architecture In-Depth** (1.5 hrs)
  - 📁 Study: [06-genai-systems/00-concepts/rag-architecture/](../../06-genai-systems/00-concepts/rag-architecture/)
  - Topics:
    - Centralized vs federated retrieval
    - Cascading retrieval (sparse → dense → reranker)
    - Streaming RAG for real-time responses
  - 📁 Reference: [RAG Architecture Cheatsheet](../cheatsheets/rag-architecture-cheatsheet.md)

- [ ] **Vector Databases & Embedding Models** (1.5 hrs)
  - 📁 Study: [06-genai-systems/00-concepts/vector-databases/](../../06-genai-systems/00-concepts/vector-databases/)
  - Topics:
    - Embedding spaces and similarity search (cosine, dot product)
    - ANN algorithms (HNSW, IVF)
    - Pinecone, Weaviate, Qdrant, pgvector comparison
    - Chunking strategies: fixed-size, semantic, recursive

### Afternoon Session (2.5-3 hrs)

- [ ] **Retriever & Ranker LLD** (1.5 hrs)
  - 📁 Study: [06-genai-systems/01-llm-lld-projects/retriever-ranker/](../../06-genai-systems/01-llm-lld-projects/retriever-ranker/)
  - Practice: Trace a query through sparse retrieval → dense retrieval → reranking

- [ ] **Document Chunker LLD** (1 hr)
  - 📁 Study: [06-genai-systems/01-llm-lld-projects/chunker-metadata-indexer/](../../06-genai-systems/01-llm-lld-projects/chunker-metadata-indexer/)
  - Practice: Design a chunker for HTML documents with metadata extraction

### Evening Review (30 min)

- [ ] Draw the full RAG pipeline from ingestion to response
- [ ] Compare centralized vs federated retrieval patterns

---

## 📅 Day 3: GenAI LLD Components

**Goal:** Build and understand core GenAI building blocks.

### Morning Session (2.5-3 hrs)

- [ ] **Prompt Builder** (1.5 hrs)
  - 📁 Study: [06-genai-systems/01-llm-lld-projects/prompt-builder/](../../06-genai-systems/01-llm-lld-projects/prompt-builder/)
  - Practice: Design a prompt builder that handles:
    - Prompt injection attacks
    - Dynamic context window management
    - Few-shot example selection

- [ ] **Conversation Memory Store** (1 hr)
  - 📁 Study: [06-genai-systems/01-llm-lld-projects/conversation-memory-store/](../../06-genai-systems/01-llm-lld-projects/conversation-memory-store/)
  - Topics: Sliding window, summary-based, and hybrid memory strategies

### Afternoon Session (2.5-3 hrs)

- [ ] **LLM Request Orchestrator** (1.5 hrs)
  - 📁 Study: [06-genai-systems/01-llm-lld-projects/llm-request-orchestrator/](../../06-genai-systems/01-llm-lld-projects/llm-request-orchestrator/)
  - Topics: Request routing, retries, fallback models, streaming

- [ ] **Safety Filter & Policy Engine** (1 hr)
  - 📁 Study: [06-genai-systems/01-llm-lld-projects/safety-filter-policy-engine/](../../06-genai-systems/01-llm-lld-projects/safety-filter-policy-engine/)
  - Practice: Design input/output filter chain with configurable policies

### Evening Review (30 min)

- [ ] Sketch class diagrams for prompt builder and orchestrator
- [ ] Identify which design patterns appear (Strategy, Chain of Responsibility, Builder)

---

## 📅 Day 4: Safety & Evaluation

**Goal:** Understand LLM safety guardrails and evaluation frameworks.

### Morning Session (2-2.5 hrs)

- [ ] **Safety & Governance** (1.5 hrs)
  - 📁 Study: [06-genai-systems/00-concepts/safety-governance/](../../06-genai-systems/00-concepts/safety-governance/)
  - Topics:
    - Hallucination detection and mitigation
    - Toxicity and content filtering
    - PII detection and redaction
    - Red-teaming strategies

- [ ] **LLM Evaluation** (1 hr)
  - 📁 Study: [06-genai-systems/00-concepts/llm-evaluation/](../../06-genai-systems/00-concepts/llm-evaluation/)
  - Topics:
    - Automated metrics (BLEU, ROUGE, BERTScore)
    - LLM-as-judge evaluation
    - Human evaluation frameworks
    - A/B testing for LLM systems

### Afternoon Session (2-2.5 hrs)

- [ ] **End-to-End Safety Pipeline Design** (1 hr)
  - Practice: Design a safety pipeline for a customer-facing chatbot
  - Include: input filtering → context grounding → output validation → logging

- [ ] **Evaluation Harness Design** (1 hr)
  - Practice: Design an offline evaluation framework
  - Include: test dataset management, metric computation, regression detection

### Evening Review (30 min)

- [ ] List the top 5 safety concerns for a production LLM system
- [ ] Compare automated vs human evaluation trade-offs

---

## 📅 Day 5: HLD — RAG-Based Enterprise Search

**Goal:** Design a complete RAG-based search system end-to-end.

### Morning Session (2.5-3 hrs)

- [ ] **Study RAG Search HLD** (1 hr)
  - 📁 Study: [06-genai-systems/02-llm-hld-projects/](../../06-genai-systems/02-llm-hld-projects/)
  - 📁 Template: [06-genai-systems/02-llm-hld-projects/GENAI-DESIGN-TEMPLATE.md](../../06-genai-systems/02-llm-hld-projects/GENAI-DESIGN-TEMPLATE.md)

- [ ] **Design Practice: Enterprise Search** (2 hrs)
  - Set a 45-min timer and design from scratch:
    1. Clarify use case and scale (5 min)
    2. Estimate token budgets and QPS (5 min)
    3. Sketch architecture: ingestion + retrieval + generation (15 min)
    4. Deep dive RAG pipeline and routing (15 min)
    5. Trade-offs and safety considerations (5 min)

### Afternoon Session (2.5-3 hrs)

- [ ] **Compare With Reference Design** (1 hr)
  - Review gaps in your design vs the reference
  - Note: Did you handle hybrid retrieval? Streaming? Caching?

- [ ] **Scaling & Cost Optimization** (1.5 hrs)
  - Topics:
    - Semantic caching to reduce LLM calls
    - Model routing (small model for simple queries, large for complex)
    - Embedding pre-computation and indexing at scale
    - GPU cluster management

### Evening Review (30 min)

- [ ] Practice explaining your RAG search design in 5 minutes
- [ ] Note the 3 most important trade-offs

---

## 📅 Day 6: HLD — Conversational AI Chatbot

**Goal:** Design a production chatbot with memory, safety, and multi-turn reasoning.

### Morning Session (2.5-3 hrs)

- [ ] **Study Chatbot HLD** (1 hr)
  - 📁 Study: [06-genai-systems/02-llm-hld-projects/](../../06-genai-systems/02-llm-hld-projects/)
  - Focus on: memory management, context window optimization, multi-turn flows

- [ ] **Design Practice: AI Chatbot** (2 hrs)
  - Set a 45-min timer:
    1. Requirements: multi-turn, grounded, safe (5 min)
    2. Token budget: context window allocation (5 min)
    3. Architecture: gateway → orchestrator → retriever → LLM → safety (15 min)
    4. Deep dive: memory store, streaming, fallback handling (15 min)
    5. Trade-offs: latency vs quality, cost controls (5 min)

### Afternoon Session (2.5-3 hrs)

- [ ] **Compare & Improve** (1 hr)
  - Review: How does this differ from the RAG search design?
  - Key differences: stateful sessions, streaming, conversation history

- [ ] **Connect to Classical HLD** (1.5 hrs)
  - Map chatbot components to classical patterns:
    - WebSocket servers → [04-hld-projects/chat-service/](../../04-hld-projects/chat-service/)
    - Message queues → async LLM inference pipeline
    - Caching → semantic response caching
    - Rate limiting → token-based rate limiting

### Evening Review (30 min)

- [ ] Explain how a chatbot system differs from a simple RAG search
- [ ] Draw the message flow for a multi-turn conversation

---

## 📅 Day 7: Mock Practice & Review

**Goal:** Test yourself under interview conditions.

### Morning Session (2 hrs)

- [ ] **GenAI Mock Interview #1** (1 hr)
  - Prompt: "Design an LLM-powered customer support system"
  - Set a 45-min timer
  - Use the 5-step GenAI design flow:
    1. Clarify use case
    2. Estimate token budgets
    3. Sketch architecture
    4. Deep dive RAG/routing
    5. Trade-offs & safety
  - 📁 Reference: [GenAI SD Framework](../../06-genai-systems/GENAI-SD-FRAMEWORK.md)
  - 📁 Reference: [GenAI System Design One-Pager](../cheatsheets/genai-system-design-one-pager.md)

- [ ] **Self-Assessment** (30 min)
  - Did you cover: retrieval, generation, safety, cost, evaluation?
  - Did you connect to classical infra (caching, queues, load balancing)?

### Afternoon Session (2 hrs)

- [ ] **GenAI Mock Interview #2** (1 hr)
  - Prompt: "Design an AI-powered code review assistant"
  - Follow the same 5-step flow

- [ ] **Cheatsheet Review** (1 hr)
  - 📁 Review: [GenAI System Design One-Pager](../cheatsheets/genai-system-design-one-pager.md)
  - 📁 Review: [RAG Architecture Cheatsheet](../cheatsheets/rag-architecture-cheatsheet.md)
  - 📁 Review: [Trade-offs Matrix](../cheatsheets/trade-offs-matrix.md)

### Evening Review (30 min)

- [ ] Identify your weakest area
- [ ] Plan extended practice if you have Week 2 available

---

## 📅 Days 8–10: Extended Practice (Optional Week 2)

### Day 8: AI Copilot HLD
- [ ] **Design: AI Coding Copilot** (3-4 hrs)
  - 📁 Study: [06-genai-systems/02-llm-hld-projects/](../../06-genai-systems/02-llm-hld-projects/)
  - Focus: IDE integration, code context retrieval, inline suggestions, streaming

### Day 9: Agentic Workflows & Advanced Patterns
- [ ] **Prompting, Tools & Agents Deep Dive** (2 hrs)
  - 📁 Study: [06-genai-systems/00-concepts/prompting-tools-agents/](../../06-genai-systems/00-concepts/prompting-tools-agents/)
- [ ] **Design: Agentic Workflow System** (2 hrs)
  - Focus: Multi-step planning, tool selection, error recovery

### Day 10: Review & Final Mocks
- [ ] **Mock Interview #3** (1 hr) — Random GenAI prompt
- [ ] **Classical + GenAI Hybrid Mock** (1 hr) — e.g., "Design YouTube with AI-powered recommendations and summarization"
- [ ] **Weak Area Review** (1-2 hrs)

---

## ✅ Checkpoints

### After Day 4 (Mid-Track)
Before continuing, ensure you can:
- [ ] Explain RAG end-to-end in 2 minutes
- [ ] List 5 GenAI-specific components and their purposes
- [ ] Describe 3 LLM safety strategies
- [ ] Estimate token costs for a given system

### After Day 7 (Track Complete)
Before interviews, ensure you can:
- [ ] Design a RAG search system in 45 minutes
- [ ] Design a chatbot system in 45 minutes
- [ ] Discuss trade-offs: cost vs latency, quality vs speed, safety vs UX
- [ ] Connect GenAI components to classical infra patterns
- [ ] Explain evaluation strategies for LLM systems

---

## 🎯 Priority Focus (If Short on Time)

**Must Master (Days 1–5):**
- RAG architecture and patterns
- Token budget estimation
- At least 1 full GenAI HLD ([Semantic Retrieval Platform](../../06-genai-systems/02-llm-hld-projects/semantic-retrieval-platform/) or [Document Q&A RAG](../../06-genai-systems/02-llm-hld-projects/document-qa-rag/))
- Safety basics (hallucination mitigation, input/output filtering)

**Should Know (Days 6–7):**
- Chatbot HLD with memory management
- Evaluation frameworks
- Mock practice under timed conditions

**Good to Know (Days 8–10):**
- AI Copilot design
- Agentic workflows
- Model routing and orchestration patterns

---

## 🔗 Quick Links

- [GenAI SD Framework](../../06-genai-systems/GENAI-SD-FRAMEWORK.md) — 6-step interview framework
- [Classic vs GenAI SD](../../06-genai-systems/CLASSIC-VS-GENAI.md) — What's different in GenAI interviews
- [GenAI Pitfalls](../../06-genai-systems/PITFALLS.md) — Top 10 interview mistakes to avoid
- [GenAI Concepts](../../06-genai-systems/00-concepts/) — Core GenAI theory
- [GenAI LLD Components](../../06-genai-systems/01-llm-lld-projects/) — Hands-on component designs
- [GenAI HLD Projects](../../06-genai-systems/02-llm-hld-projects/) — Full system designs
- [GenAI System Design One-Pager](../cheatsheets/genai-system-design-one-pager.md) — Interview cheatsheet
- [RAG Architecture Cheatsheet](../cheatsheets/rag-architecture-cheatsheet.md) — RAG quick reference
- [Classical HLD Projects](../../04-hld-projects/) — Traditional system designs

---

*Ready to ace your GenAI system design interview! 🚀*
