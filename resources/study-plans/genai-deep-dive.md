# 🧠 GenAI Deep Dive (4 Weeks)

A comprehensive 4-week plan for thorough GenAI system design interview preparation, integrating concepts, LLDs, HLDs, and safety/evaluation.

---

## 📋 Overview

| Week | Focus Area | Hours/Week | Topics |
|------|------------|------------|--------|
| 1 | GenAI Foundations & Concepts | 15-20 hrs | LLM basics, RAG, vector DBs, embeddings, prompting |
| 2 | GenAI LLD Components | 18-22 hrs | Chunker, retriever, prompt builder, memory, orchestrator, safety filter |
| 3 | GenAI HLD Systems | 20-25 hrs | semantic retrieval, RAG search, chatbot, AI copilot, content moderation |
| 4 | Advanced Topics + Mock Practice | 15-20 hrs | Agentic workflows, evaluation, mocks, classical integration |

**Total Time:** ~70–90 hours over 4 weeks

---

## 📅 Week 1: GenAI Foundations & Concepts

**Goal:** Build a deep understanding of GenAI-specific concepts and how they differ from classical system design.

### Day 1 (Monday): LLM-Oriented System Design

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **LLM System Design Fundamentals** | [06-genai-systems/00-concepts/llm-system-design/](../../06-genai-systems/00-concepts/llm-system-design/) |
| | - How LLM inference works (tokenization → attention → decoding) | |
| | - Cost model: input tokens, output tokens, model tiers | |
| | - Latency characteristics (time to first token, tokens per second) | |
| 1.5 hrs | **Classical → GenAI Mapping** | [06-genai-systems/README.md](../../06-genai-systems/README.md) |
| | - How caching, load balancing, queues apply to LLM systems | |
| | - New components: vector DBs, embedding services, safety filters | |

**Practice:**
- [ ] Estimate the cost of 1M daily LLM API calls with average 500 input + 200 output tokens
- [ ] Compare latency of LLM call vs traditional DB query — what are the implications?
- [ ] List 5 ways GenAI system design differs from classical system design

---

### Day 2 (Tuesday): RAG Architecture

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **RAG Fundamentals** | [06-genai-systems/00-concepts/rag-architecture/](../../06-genai-systems/00-concepts/rag-architecture/) |
| | - Retrieval-Augmented Generation end-to-end | |
| | - Why RAG vs fine-tuning vs prompt-only | |
| | - Ingestion pipeline: chunk → embed → index | |
| | - Query pipeline: embed → retrieve → rerank → generate | |
| 1 hr | **RAG Patterns** | [RAG Architecture Cheatsheet](../cheatsheets/rag-architecture-cheatsheet.md) |
| | - Centralized, federated, cascading, streaming | |
| | - Hybrid retrieval (sparse + dense) | |

**Practice:**
- [ ] Draw the complete RAG pipeline (ingestion + query)
- [ ] Explain when to use centralized vs federated retrieval
- [ ] Compare BM25 (sparse) vs vector search (dense) — when to use each

---

### Day 3 (Wednesday): Vector Databases & Embeddings

| Time | Topic | Resources |
|------|-------|-----------|
| 1.5 hrs | **Vector Databases** | [06-genai-systems/00-concepts/vector-databases/](../../06-genai-systems/00-concepts/vector-databases/) |
| | - Embedding spaces and similarity metrics | |
| | - ANN algorithms: HNSW, IVF, PQ | |
| | - Technology comparison: Pinecone, Weaviate, Qdrant, pgvector, Milvus | |
| 1.5 hrs | **Chunking & Embedding Strategies** | [06-genai-systems/00-concepts/vector-databases/](../../06-genai-systems/00-concepts/vector-databases/) |
| | - Fixed-size, semantic, recursive chunking | |
| | - Chunk overlap and its effects | |
| | - Embedding model selection (dimension, speed, quality) | |
| | - Metadata enrichment for filtered retrieval | |

**Practice:**
- [ ] Design a chunking strategy for a corpus of PDF research papers
- [ ] Compare 3 vector database options for a 10M document enterprise use case
- [ ] Calculate storage requirements: 10M documents × 1536-dim embeddings × float32

---

### Day 4 (Thursday): Prompting, Tools & Agents

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Prompt Engineering** | [06-genai-systems/00-concepts/prompting-tools-agents/](../../06-genai-systems/00-concepts/prompting-tools-agents/) |
| | - System prompts and role-based prompting | |
| | - Few-shot and chain-of-thought techniques | |
| | - Structured output (JSON mode, function calling) | |
| 1.5 hrs | **Tool-Using Agents** | [06-genai-systems/00-concepts/prompting-tools-agents/](../../06-genai-systems/00-concepts/prompting-tools-agents/) |
| | - Function calling and tool integration | |
| | - Agent planning patterns (ReAct, Plan-and-Execute) | |
| | - Multi-agent collaboration | |

**Practice:**
- [ ] Write a system prompt for a customer support agent with tool access
- [ ] Design the tool selection logic for an agent with 10+ available tools
- [ ] Compare single-agent vs multi-agent architectures — trade-offs

---

### Day 5 (Friday): Safety & Governance

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **LLM Safety** | [06-genai-systems/00-concepts/safety-governance/](../../06-genai-systems/00-concepts/safety-governance/) |
| | - Hallucination detection and mitigation strategies | |
| | - Input/output content filtering | |
| | - PII detection and redaction | |
| | - Prompt injection attacks and defenses | |
| 1 hr | **Governance & Compliance** | [06-genai-systems/00-concepts/safety-governance/](../../06-genai-systems/00-concepts/safety-governance/) |
| | - Audit logging for LLM interactions | |
| | - Red-teaming and adversarial testing | |
| | - Responsible AI principles | |

**Practice:**
- [ ] Design a 4-layer safety pipeline (input → retrieval → output → monitoring)
- [ ] List 5 prompt injection attack patterns and their defenses
- [ ] Explain how to detect and handle hallucinations in a RAG system

---

### Day 6 (Saturday): LLM Evaluation

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Evaluation Frameworks** | [06-genai-systems/00-concepts/llm-evaluation/](../../06-genai-systems/00-concepts/llm-evaluation/) |
| | - Automated metrics: BLEU, ROUGE, BERTScore, faithfulness | |
| | - LLM-as-judge approaches | |
| | - Human evaluation design | |
| | - RAG-specific metrics: context relevance, answer faithfulness | |
| 1 hr | **A/B Testing for LLM Systems** | [06-genai-systems/00-concepts/llm-evaluation/](../../06-genai-systems/00-concepts/llm-evaluation/) |
| | - Online vs offline evaluation | |
| | - Metric selection for GenAI products | |
| | - Regression detection and alerting | |

**Practice:**
- [ ] Design an evaluation harness for a RAG chatbot
- [ ] Compare 3 evaluation approaches for a code generation system
- [ ] List metrics you would track for a production LLM API

---

### Day 7 (Sunday): Week 1 Review

| Time | Activity |
|------|----------|
| 1.5 hrs | Review all concepts — create a personal summary sheet |
| 1 hr | Practice explaining RAG, safety, and evaluation out loud (5 min each) |
| 30 min | Identify weak areas for deeper study in later weeks |

---

### Week 1 Checkpoint ✅

Before moving to Week 2, ensure you can:
- [ ] Explain RAG architecture end-to-end with component names
- [ ] Compare vector database options with trade-offs
- [ ] Describe 3+ chunking strategies and when to use each
- [ ] List safety concerns and mitigation strategies for LLM systems
- [ ] Explain LLM evaluation approaches and key metrics
- [ ] Estimate token costs and latency for a given workload

---

## 📅 Week 2: GenAI LLD Components

**Goal:** Build deep understanding of individual GenAI components through hands-on study.

### Day 8 (Monday): Document Chunker & Metadata Indexer

| Time | Topic | Resources |
|------|-------|-----------|
| 2.5 hrs | **Chunker LLD** | [06-genai-systems/01-llm-lld-projects/chunker-metadata-indexer/](../../06-genai-systems/01-llm-lld-projects/chunker-metadata-indexer/) |
| | - Chunking strategies: fixed, semantic, recursive | |
| | - Metadata extraction and enrichment | |
| | - Document format handling (PDF, HTML, Markdown) | |
| 1 hr | **Practice** | |
| | - Design a chunker for a knowledge base with mixed document types | |
| | - Handle edge cases: tables, code blocks, images with captions | |

**Key Design Patterns:** Strategy (chunking algorithms), Builder (chunk configuration)

---

### Day 9 (Tuesday): Retriever & Ranker

| Time | Topic | Resources |
|------|-------|-----------|
| 2.5 hrs | **Retriever & Ranker LLD** | [06-genai-systems/01-llm-lld-projects/retriever-ranker/](../../06-genai-systems/01-llm-lld-projects/retriever-ranker/) |
| | - Sparse retrieval (BM25, TF-IDF) | |
| | - Dense retrieval (vector similarity) | |
| | - Hybrid retrieval and fusion strategies | |
| | - Cross-encoder reranking | |
| 1.5 hrs | **Practice** | |
| | - Design a hybrid retriever with configurable weights | |
| | - Trace a query through: BM25 → vector search → reciprocal rank fusion → reranker | |

**Key Design Patterns:** Strategy (retrieval algorithms), Chain of Responsibility (reranking pipeline)

---

### Day 10 (Wednesday): Prompt Builder

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Prompt Builder LLD** | [06-genai-systems/01-llm-lld-projects/prompt-builder/](../../06-genai-systems/01-llm-lld-projects/prompt-builder/) |
| | - Dynamic context window management | |
| | - Template composition and variable injection | |
| | - Few-shot example selection and ordering | |
| | - Token counting and truncation strategies | |
| 1.5 hrs | **Practice** | |
| | - Design a prompt builder for a multi-source RAG system | |
| | - Handle: system prompt + retrieved context + conversation history + user query | |
| | - Implement priority-based truncation when exceeding token limits | |

**Key Design Patterns:** Builder (prompt construction), Template Method (prompt templates)

---

### Day 11 (Thursday): Conversation Memory Store

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Memory Store LLD** | [06-genai-systems/01-llm-lld-projects/conversation-memory-store/](../../06-genai-systems/01-llm-lld-projects/conversation-memory-store/) |
| | - Sliding window memory | |
| | - Summary-based memory (periodic summarization) | |
| | - Hybrid: recent messages + older summaries | |
| | - Cross-session memory and user preferences | |
| 1.5 hrs | **Practice** | |
| | - Design a memory store for a customer support chatbot | |
| | - Handle: 50+ turn conversations, session persistence, token budget | |

**Key Design Patterns:** Strategy (memory strategies), Decorator (memory layers)

---

### Day 12 (Friday): LLM Request Orchestrator

| Time | Topic | Resources |
|------|-------|-----------|
| 2.5 hrs | **Orchestrator LLD** | [06-genai-systems/01-llm-lld-projects/llm-request-orchestrator/](../../06-genai-systems/01-llm-lld-projects/llm-request-orchestrator/) |
| | - Request routing and model selection | |
| | - Retry logic with exponential backoff | |
| | - Fallback chains (primary → secondary → cached) | |
| | - Streaming response handling | |
| | - Token budget enforcement | |
| 1.5 hrs | **Practice** | |
| | - Design an orchestrator supporting 3 model tiers | |
| | - Implement circuit breaker for LLM provider failures | |

**Key Design Patterns:** Strategy (model routing), Chain of Responsibility (fallback), Observer (streaming)

---

### Day 13 (Saturday): Safety Filter & Policy Engine

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Safety Filter LLD** | [06-genai-systems/01-llm-lld-projects/safety-filter-policy-engine/](../../06-genai-systems/01-llm-lld-projects/safety-filter-policy-engine/) |
| | - Input validation and sanitization | |
| | - Output content filtering | |
| | - PII detection and redaction | |
| | - Policy engine with configurable rules | |
| 2 hrs | **Integration Practice** | |
| | - Connect safety filter with orchestrator and prompt builder | |
| | - Design the full request lifecycle: input filter → build prompt → call LLM → output filter | |

**Key Design Patterns:** Chain of Responsibility (filter pipeline), Strategy (filter types)

---

### Day 14 (Sunday): Week 2 Review + Component Integration

| Time | Activity |
|------|----------|
| 2 hrs | **Integration Exercise**: Design the component interaction for a RAG pipeline |
| | Connect: Chunker → Retriever → Prompt Builder → Orchestrator → Safety Filter |
| 1 hr | **Review**: Which design patterns appear across components? |
| 30 min | **Self-assessment**: Can you design each component from scratch in 20 minutes? |

---

### Week 2 Checkpoint ✅

Before moving to Week 3, ensure you can:
- [ ] Design each GenAI LLD component from scratch
- [ ] Explain the interfaces between components
- [ ] Identify design patterns used in each component
- [ ] Handle edge cases: token limits, provider failures, safety violations
- [ ] Connect components into a working pipeline

---

## 📅 Week 3: GenAI HLD Systems

**Goal:** Design complete GenAI systems end-to-end, applying concepts and components from Weeks 1–2.

### Day 15 (Monday): GenAI HLD Framework

| Time | Topic | Resources |
|------|-------|-----------|
| 1 hr | **GenAI Design Template** | [06-genai-systems/02-llm-hld-projects/GENAI-DESIGN-TEMPLATE.md](../../06-genai-systems/02-llm-hld-projects/GENAI-DESIGN-TEMPLATE.md) |
| | - 5-step GenAI design flow | |
| | - How GenAI HLD differs from classical HLD | |
| 1 hr | **GenAI SD Framework** | [06-genai-systems/GENAI-SD-FRAMEWORK.md](../../06-genai-systems/GENAI-SD-FRAMEWORK.md) |
| | - 6-step reusable interview framework | |
| | - Worked example: Enterprise Document Q&A | |
| 1 hr | **GenAI One-Pager Review** | [GenAI System Design One-Pager](../cheatsheets/genai-system-design-one-pager.md) |
| | - Memorize the 5-step interview flow | |
| 1 hr | **Classical HLD Refresher** | [04-hld-projects/DESIGN-TEMPLATE.md](../../04-hld-projects/DESIGN-TEMPLATE.md) |
| | - Review how classical HLD patterns integrate with GenAI | |

**Practice:**
- [ ] Compare classical HLD template with GenAI design template
- [ ] List which classical components reappear in GenAI systems

---

### Day 16–17 (Tue–Wed): RAG-Based Enterprise Search

| Time | Topic | Resources |
|------|-------|-----------|
| 3 hrs (Day 16) | **Study: Semantic Retrieval + RAG Search HLD** | [Semantic Retrieval Platform](../../06-genai-systems/02-llm-hld-projects/semantic-retrieval-platform/) · [Document Q&A (RAG)](../../06-genai-systems/02-llm-hld-projects/document-qa-rag/) |
| | - Requirements and scale estimation | |
| | - Ingestion pipeline architecture | |
| | - Query pipeline with hybrid retrieval | |
| | - Streaming response delivery | |
| 3.5 hrs (Day 17) | **Design Practice + Deep Dives** | |
| | - Timed design (45 min) | |
| | - Deep dive: semantic caching, embedding refresh, multi-tenant indexing | |
| | - Scaling: GPU provisioning, index partitioning, cost optimization | |

**Key Architecture Decisions:**
- Embedding model selection and index type
- Retrieval strategy: sparse, dense, or hybrid
- Streaming vs batch response
- Multi-tenant data isolation

---

### Day 18–19 (Thu–Fri): Conversational AI Chatbot

| Time | Topic | Resources |
|------|-------|-----------|
| 3 hrs (Day 18) | **Study: Chatbot HLD** | [06-genai-systems/02-llm-hld-projects/](../../06-genai-systems/02-llm-hld-projects/) |
| | - Multi-turn conversation management | |
| | - Memory and context window optimization | |
| | - Safety pipeline integration | |
| | - WebSocket-based streaming | |
| 3.5 hrs (Day 19) | **Design Practice + Integration** | |
| | - Timed design (45 min) | |
| | - Connect to classical chat service: [04-hld-projects/chat-service/](../../04-hld-projects/chat-service/) | |
| | - Deep dive: session management, handoff to human agents, feedback loops | |

**Key Architecture Decisions:**
- Memory strategy for long conversations
- Streaming vs request-response delivery
- Safety filter placement (pre-LLM, post-LLM, or both)
- Escalation to human agents

---

### Day 20 (Saturday): AI Coding Copilot

| Time | Topic | Resources |
|------|-------|-----------|
| 3.5 hrs | **Study + Design: AI Copilot** | [06-genai-systems/02-llm-hld-projects/](../../06-genai-systems/02-llm-hld-projects/) |
| | - IDE integration architecture | |
| | - Code context retrieval (AST parsing, semantic search) | |
| | - Inline suggestion streaming | |
| | - Multi-file context management | |
| | - Timed design practice (45 min) | |

**Key Architecture Decisions:**
- How to extract relevant code context (current file, imports, related files)
- Streaming suggestions with low latency
- Caching frequently suggested patterns
- Privacy and security for enterprise code

---

### Day 21 (Sunday): Content Moderation + Week 3 Review

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Design: Content Moderation Pipeline** | [06-genai-systems/02-llm-hld-projects/](../../06-genai-systems/02-llm-hld-projects/) |
| | - Multi-modal content analysis | |
| | - Tiered moderation (automated → LLM → human) | |
| | - Policy engine and decision logging | |
| 1.5 hrs | **Week 3 Review** | |
| | - Compare all 4 GenAI HLD systems | |
| | - Common components and patterns across systems | |
| | - Identify your strongest and weakest design | |

---

### Week 3 Checkpoint ✅

Before moving to Week 4, ensure you can:
- [ ] Design semantic retrieval infrastructure and RAG search in 45 minutes with all major components
- [ ] Design a chatbot with memory, safety, and streaming
- [ ] Design an AI copilot with code-aware retrieval
- [ ] Explain content moderation pipeline with escalation paths
- [ ] Connect GenAI systems to classical infrastructure patterns

---

## 📅 Week 4: Advanced Topics + Mock Practice

**Goal:** Cover advanced patterns, practice under interview conditions, and solidify integration with classical system design.

### Day 22 (Monday): Agentic Workflows

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Agentic System Design** | [06-genai-systems/00-concepts/prompting-tools-agents/](../../06-genai-systems/00-concepts/prompting-tools-agents/) |
| | - Multi-step planning and execution | |
| | - Tool orchestration and error recovery | |
| | - Agentic loops with safety bounds | |
| 2 hrs | **Design Practice** | |
| | - Design an agentic workflow system for automated data analysis | |
| | - Include: planning, tool selection, execution, self-correction | |

---

### Day 23 (Tuesday): Model Routing & Cost Optimization

| Time | Topic | Resources |
|------|-------|-----------|
| 2 hrs | **Model Routing Patterns** | [06-genai-systems/00-concepts/model-routing-orchestration/](../../06-genai-systems/00-concepts/model-routing-orchestration/) |
| | - Query complexity classification | |
| | - Small model → large model cascading | |
| | - Semantic caching for repeated queries | |
| | - Batch inference for non-real-time workloads | |
| 2 hrs | **Cost Optimization Practice** | [06-genai-systems/00-concepts/token-cost-latency/](../../06-genai-systems/00-concepts/token-cost-latency/) |
| | - Design a cost-optimized inference pipeline | |
| | - Calculate: what % cost reduction from caching + routing? | |

---

### Day 24 (Wednesday): Classical + GenAI Integration

| Time | Topic | Resources |
|------|-------|-----------|
| 3.5 hrs | **Augmenting Classical Systems with LLMs** | |
| | - URL Shortener + AI-powered link summarization | [04-hld-projects/url-shortener/](../../04-hld-projects/url-shortener/) |
| | - E-commerce + AI product recommendations and search | [04-hld-projects/ecommerce-backend/](../../04-hld-projects/ecommerce-backend/) |
| | - Chat Service + AI support bot integration | [04-hld-projects/chat-service/](../../04-hld-projects/chat-service/) |
| | - Video Streaming + AI summarization and search | [04-hld-projects/video-streaming/](../../04-hld-projects/video-streaming/) |
| | - Ride Sharing + AI support and ETA explanation | [04-hld-projects/ride-sharing/](../../04-hld-projects/ride-sharing/) |

**Practice:**
- [ ] For each classical system, describe 1–2 GenAI extensions
- [ ] Design the integration points (where does the LLM fit in the architecture?)

---

### Day 25 (Thursday): Mock Interview Day #1

| Time | Activity |
|------|----------|
| 1.5 hrs | **GenAI Mock #1** — "Design an LLM-powered enterprise knowledge base" (45 min + review) |
| 1.5 hrs | **GenAI Mock #2** — "Design an AI customer support system" (45 min + review) |
| 1 hr | **Self-Assessment** — Note strengths, weaknesses, time management |

---

### Day 26 (Friday): Mock Interview Day #2

| Time | Activity |
|------|----------|
| 1.5 hrs | **GenAI Mock #3** — "Design a content moderation system using LLMs" (45 min + review) |
| 1.5 hrs | **Hybrid Mock** — "Design Netflix with AI-powered search and recommendations" (45 min + review) |
| 1 hr | **Compare with Day 25** — Track improvement |

---

### Day 27 (Saturday): Deep Review

| Time | Activity | Resources |
|------|----------|-----------|
| 1 hr | **Cheatsheet Review** | [Cheatsheets](../cheatsheets/) |
| | - GenAI System Design One-Pager | |
| | - RAG Architecture Cheatsheet | |
| | - Trade-offs Matrix | |
| 1 hr | **Concept Review** | [06-genai-systems/00-concepts/](../../06-genai-systems/00-concepts/) |
| 1 hr | **Weak Areas** | Focus on identified gaps from mocks |
| 1 hr | **Trade-offs Practice** | Review all GenAI-specific trade-offs |

---

### Day 28 (Sunday): Final Preparation

| Time | Activity |
|------|----------|
| 1 hr | **Quick Concept Drill** — 2 min per GenAI concept |
| 1 hr | **Quick System Drill** — 5 min per GenAI HLD system, including retrieval-only infrastructure |
| 30 min | **Token Budget Estimation Practice** — 3 scenarios |
| 30 min | **Final Checklist** — Everything ready for interview |

---

### Week 4 Checkpoint ✅

Before the interview, ensure you can:
- [ ] Design any GenAI system in 45 minutes
- [ ] Handle curveball questions about cost, safety, and evaluation
- [ ] Integrate GenAI components into classical system designs
- [ ] Explain model routing and cost optimization strategies
- [ ] Discuss agentic workflows with safety bounds
- [ ] Manage time effectively during timed practice

---

## 📈 Full Month Progress Tracker

```markdown
## My GenAI Deep Dive Progress

### Week 1: Foundations & Concepts
- [ ] Day 1: LLM System Design Fundamentals
- [ ] Day 2: RAG Architecture
- [ ] Day 3: Vector Databases & Embeddings
- [ ] Day 4: Prompting, Tools & Agents
- [ ] Day 5: Safety & Governance
- [ ] Day 6: LLM Evaluation
- [ ] Day 7: Week 1 Review

### Week 2: LLD Components
- [ ] Day 8: Document Chunker & Metadata Indexer
- [ ] Day 9: Retriever & Ranker
- [ ] Day 10: Prompt Builder
- [ ] Day 11: Conversation Memory Store
- [ ] Day 12: LLM Request Orchestrator
- [ ] Day 13: Safety Filter & Policy Engine
- [ ] Day 14: Week 2 Review + Integration

### Week 3: HLD Systems
- [ ] Day 15: GenAI HLD Framework
- [ ] Day 16–17: RAG-Based Enterprise Search
- [ ] Day 18–19: Conversational AI Chatbot
- [ ] Day 20: AI Coding Copilot
- [ ] Day 21: Content Moderation + Review

### Week 4: Advanced + Practice
- [ ] Day 22: Agentic Workflows
- [ ] Day 23: Model Routing & Cost Optimization
- [ ] Day 24: Classical + GenAI Integration
- [ ] Day 25: Mock Day #1
- [ ] Day 26: Mock Day #2
- [ ] Day 27: Deep Review
- [ ] Day 28: Final Preparation
```

---

## 🎯 Accelerated Plans

### 2-Week Plan (Skip Week 1)
If you already understand LLM fundamentals:
- **Week 1** → Week 2 content (LLD Components)
- **Week 2** → Weeks 3–4 content (HLD Systems + Practice)

### 3-Week Plan (Condensed)
- **Week 1** → Key concepts (Days 1, 2, 5) + 3 LLD components
- **Week 2** → All 4 HLD systems
- **Week 3** → Advanced topics + Mock practice

### Already Done Classical System Design?
Jump straight to this plan. Your classical knowledge will give you a head start on infrastructure patterns (caching, queues, load balancing) — focus your energy on GenAI-specific concepts and components.

---

## 📌 Key Success Factors

1. **Build on classical foundations** — GenAI systems use the same infra primitives
2. **Practice estimation** — Token budgets, cost per query, and latency are key interview topics
3. **Think about safety first** — Interviewers expect you to raise safety concerns proactively
4. **Connect components** — Show you understand how chunker, retriever, builder, and orchestrator work together
5. **Stay current** — GenAI patterns evolve quickly; review latest best practices

---

## 🔗 Quick Links

- [GenAI SD Framework](../../06-genai-systems/GENAI-SD-FRAMEWORK.md) — 6-step interview framework
- [Classic vs GenAI SD](../../06-genai-systems/CLASSIC-VS-GENAI.md) — What's different in GenAI interviews
- [GenAI Pitfalls](../../06-genai-systems/PITFALLS.md) — Top 10 interview mistakes to avoid
- [GenAI Systems Section](../../06-genai-systems/) — All GenAI content
- [GenAI Concepts](../../06-genai-systems/00-concepts/) — Core theory
- [GenAI LLD Components](../../06-genai-systems/01-llm-lld-projects/) — Component designs
- [GenAI HLD Projects](../../06-genai-systems/02-llm-hld-projects/) — Full system designs
- [GenAI System Design One-Pager](../cheatsheets/genai-system-design-one-pager.md) — Interview cheatsheet
- [RAG Architecture Cheatsheet](../cheatsheets/rag-architecture-cheatsheet.md) — RAG quick reference
- [Classical HLD Projects](../../04-hld-projects/) — Traditional system designs
- [GenAI Crash Track](genai-crash-track.md) — Shorter 1–2 week plan

---

*Four weeks of focused GenAI study will set you apart in modern system design interviews! 🚀*
