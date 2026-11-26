# 🤖 Generative AI Systems

> **Design, build, and evaluate LLM-powered systems for modern system design interviews**

Modern system design interviews increasingly feature prompts like *"Design ChatGPT"*, *"Design an LLM-powered enterprise search"*, or *"Design an AI copilot."* This section equips you with the concepts, component-level designs, and full system architectures you need to answer them confidently.

---

## 📑 Table of Contents

- [🎯 Why GenAI System Design?](#-why-genai-system-design)
- [📂 Section Structure](#-section-structure)
- [🚀 Recommended Entry Points](#-recommended-entry-points)
- [🔗 How This Ties into the Rest of the Repo](#-how-this-ties-into-the-rest-of-the-repo)
- [✅ Progress Tracker](#-progress-tracker)

---

## 🎯 Why GenAI System Design?

Interviewers now expect fluency with:

| Topic | What They Expect |
|-------|------------------|
| **RAG Architecture** | End-to-end retrieval-augmented generation pipelines |
| **Agentic Workflows** | Tool-using LLM agents with planning and memory |
| **LLM Safety & Evaluation** | Hallucination mitigation, toxicity filters, red-teaming |
| **Cost & Latency Trade-offs** | Token budgeting, model routing, KV-Cache management |
| **Scalability** | Serving LLMs at scale, streaming, batching |

This section bridges the gap between classical distributed systems knowledge (covered in [03-hld-concepts](../03-hld-concepts/) and [04-hld-projects](../04-hld-projects/)) and the GenAI-specific patterns demanded by 2025–2026 interview loops.

---

## 📂 Section Structure

```
06-genai-systems/
├── 📚 00-concepts/              # GenAI-specific concepts & patterns
│   └── (RAG, vector DBs, LLM safety, evaluation, model routing, …)
│
├── 🏗️ 01-llm-lld-projects/      # Component-level LLD exercises (Python-first)
│   └── (Chunker, embedding service, retriever, prompt builder, …)
│
├── 🌐 02-llm-hld-projects/      # Full GenAI system designs
│   └── (RAG system, AI copilot, enterprise search, chatbot, …)
│
├── 📊 diagrams/                 # Mermaid (.mmd) diagram sources
├── AGENTS.md                    # Authoritative guidance for this section
└── README.md                    # ← You are here
```

| Subfolder | Content | Status |
|-----------|---------|--------|
| [00-concepts](./00-concepts/) | GenAI concepts & trade-offs | ✅ 14 concepts; currentness ledger/checker active |
| [01-llm-lld-projects](./01-llm-lld-projects/) | Python-first LLD components | ✅ 17 of 17 shipped; practice parity refresh active |
| [02-llm-hld-projects](./02-llm-hld-projects/) | Full GenAI system designs | ✅ 8 projects; currentness/evaluation refresh active |

Inventory is complete by current folder count. Volatile provider/model/pricing/safety claims are tracked in [`../resources/GENAI-CURRENTNESS-LEDGER.md`](../resources/GENAI-CURRENTNESS-LEDGER.md) and validated with `python3 -B scripts/check_genai_currentness.py`.

### 📄 Section-Level Documents

| Document | Description |
|----------|-------------|
| [GENAI-SD-FRAMEWORK.md](./GENAI-SD-FRAMEWORK.md) | 🆕 **How to Answer Any GenAI SD Question** — Reusable 6-step interview framework with worked example |
| [CLASSIC-VS-GENAI.md](./CLASSIC-VS-GENAI.md) | 🆕 **Classic vs GenAI SD Comparison** — Side-by-side: how GenAI interviews differ from classic SD |
| [PITFALLS.md](./PITFALLS.md) | 🆕 **Top 10 Interview Pitfalls** — Common GenAI SD mistakes and how to avoid them |

---

## 🚀 Recommended Entry Points

### New to GenAI System Design?
Start with the **[GenAI SD Framework](./GENAI-SD-FRAMEWORK.md)** for a reusable 6-step approach to any GenAI interview question, then dive into **[00-concepts](./00-concepts/)**.

### Already Comfortable with Classical HLD?
Start with **[00-concepts](./00-concepts/)** to learn GenAI-specific building blocks (RAG, vector databases, LLM evaluation), then move to the HLD projects.

### Want Hands-On Practice First?
Jump into **[01-llm-lld-projects](./01-llm-lld-projects/)** to build individual GenAI components (chunkers, retrievers, prompt builders) before tackling full systems.

### Preparing for a Specific Interview Prompt?
Go straight to **[02-llm-hld-projects](./02-llm-hld-projects/)** and pick the system closest to your expected question, then backfill concepts as needed.

### Suggested Learning Flow

```
03-hld-concepts/            → Classical distributed systems foundations
      ↓
GENAI-SD-FRAMEWORK.md       → Learn the 6-step GenAI interview framework
      ↓
06-genai-systems/00-concepts/   → GenAI-specific concepts & patterns
      ↓
06-genai-systems/01-llm-lld-projects/ → Build GenAI components
      ↓
06-genai-systems/02-llm-hld-projects/ → Design full GenAI systems
      ↓
CLASSIC-VS-GENAI.md + PITFALLS.md   → Review differences & avoid pitfalls
```

---

## 🔗 How This Ties into the Rest of the Repo

GenAI systems don't exist in a vacuum—they rely on the same distributed systems primitives covered elsewhere in this repository.

| Classical Section | GenAI Relevance |
|-------------------|-----------------|
| [03-hld-concepts/caching](../03-hld-concepts/caching/) | KV-Cache, semantic caching for LLM responses |
| [03-hld-concepts/load-balancing](../03-hld-concepts/load-balancing/) | Model-aware routing, GPU load balancing |
| [03-hld-concepts/message-queues](../03-hld-concepts/message-queues/) | Async inference pipelines, feedback loops |
| [03-hld-concepts/monitoring-observability](../03-hld-concepts/monitoring-observability/) | Prompt flow tracing, model routing metrics, safety dashboards |
| [03-hld-concepts/rate-limiting](../03-hld-concepts/rate-limiting/) | Token-based rate limiting, cost controls |
| [03-hld-concepts/api-gateway](../03-hld-concepts/api-gateway/) | LLM API gateway, model versioning |
| [04-hld-projects](../04-hld-projects/) | Classical system design patterns reused in GenAI HLD |
| [01-design-patterns](../01-design-patterns/) | Strategy (model routing), Chain of Responsibility (safety filters), Observer (streaming) |

---

## ✅ Progress Tracker

### GenAI Concepts
- [x] RAG Architecture
- [x] LLM-Oriented System Design
- [x] Prompting, Tools & Agents
- [x] Safety & Governance
- [x] LLM Evaluation
- [x] Model Generalization
- [x] Safety, Evaluation & Governance (consolidated reference)
- [x] Vector Databases
- [x] Model Routing & Orchestration
- [x] Streaming & KV-Cache
- [x] Token / Cost / Latency Planning
- [x] GenAI Design Patterns

### GenAI LLD Components
- [x] Document Chunker & Metadata Indexer
- [x] Embedding Service
- [x] Retriever & Ranker
- [x] Prompt Builder
- [x] Conversation Memory Store
- [x] Tool Router
- [x] Safety Filter & Policy Engine
- [x] LLM Request Orchestrator
- [x] Evaluation Harness
- [x] Streaming Token Aggregator
- [x] Semantic Embedding Cache
- [x] Speculative Decoding Cache
- [x] Multi-Agent Orchestrator
- [x] Context Window Manager
- [x] Token Streaming Server
- [x] AI Safety Guardrails
- [x] Vector Store & Inverted Index

### GenAI HLD Systems
- [x] [Document Q&A (RAG)](./02-llm-hld-projects/document-qa-rag/)
- [x] [Multi-Tenant Chat Assistant](./02-llm-hld-projects/multi-tenant-chat-assistant/)
- [x] [AI Coding Copilot](./02-llm-hld-projects/ai-coding-copilot/)
- [x] [Agentic Workflow Orchestrator](./02-llm-hld-projects/agentic-workflow-orchestrator/)
- [x] [LLM Evaluation & Benchmark Platform](./02-llm-hld-projects/llm-eval-benchmark-platform/)
- [ ] [Semantic Retrieval Platform](./02-llm-hld-projects/semantic-retrieval-platform/) ⚠️
- [x] [LLM Inference Serving Engine](./02-llm-hld-projects/llm-inference-serving-engine/)
- [x] [Multi-Tenant Enterprise RAG](./02-llm-hld-projects/multi-tenant-enterprise-rag/)

---

## 🧭 Section Navigation

| | |
|---|---|
| **Prerequisites** | [HLD Concepts ←](../03-hld-concepts/) · [HLD Projects ←](../04-hld-projects/) — classical distributed systems knowledge |
| **What's Next** | [Case Studies →](../case-studies/) — real-world architecture deep dives |
| **Related** | [Cheatsheets](../resources/cheatsheets/) · [Study Plans](../resources/study-plans/) |

---

<p align="center">
  <b>Ready to design the next generation of AI systems? Let's go! 🚀</b>
</p>
