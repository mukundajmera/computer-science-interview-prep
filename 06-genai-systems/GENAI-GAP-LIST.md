# GenAI Track — Gap Analysis

> **Purpose:** Track folder-count completeness of every artifact in `06-genai-systems/` so contributors can pick up missing work quickly. Volatile provider/model/pricing/safety claims are tracked in [`../resources/GENAI-CURRENTNESS-LEDGER.md`](../resources/GENAI-CURRENTNESS-LEDGER.md) and checked with `python3 -B scripts/check_genai_currentness.py`.
>
> **Last updated:** 2026-06-14

## Status Legend

| Icon | Meaning |
|------|---------|
| ✅   | Done — content exists and is complete |
| 🔜   | Missing — directory or files not yet created |
| ⚠️   | Incomplete — exists but needs expansion |

---

## Gap Table

| Subsection | Item | File path | Status | Notes |
|---|---|---|---|---|
| **00-concepts** | agents-mcp-memory | `00-concepts/agents-mcp-memory/` | ✅ done | |
| **00-concepts** | fine-tuning-and-adaptation | `00-concepts/fine-tuning-and-adaptation/` | ✅ done | |
| **00-concepts** | genai-design-patterns | `00-concepts/genai-design-patterns/` | ✅ done | |
| **00-concepts** | inference-serving | `00-concepts/inference-serving/` | ✅ done | |
| **00-concepts** | llm-evaluation | `00-concepts/llm-evaluation/` | ✅ done | |
| **00-concepts** | llm-system-design | `00-concepts/llm-system-design/` | ✅ done | |
| **00-concepts** | llmops-observability | `00-concepts/llmops-observability/` | ✅ done | |
| **00-concepts** | ml-generalization | `00-concepts/ml-generalization/` | ✅ done | |
| **00-concepts** | model-adaptation-lora | `00-concepts/model-adaptation-lora/` | ✅ done | |
| **00-concepts** | model-routing-orchestration | `00-concepts/model-routing-orchestration/` | ✅ done | |
| **00-concepts** | prompting-tools-agents | `00-concepts/prompting-tools-agents/` | ✅ done | |
| **00-concepts** | rag-architecture | `00-concepts/rag-architecture/` | ✅ done | |
| **00-concepts** | rope-positional-embedding | `00-concepts/rope-positional-embedding/` | ✅ done | |
| **00-concepts** | safety-eval | `00-concepts/safety-eval/` | ✅ done | |
| **00-concepts** | safety-governance | `00-concepts/safety-governance/` | ✅ done | |
| **00-concepts** | streaming-kv-cache | `00-concepts/streaming-kv-cache/` | ✅ done | |
| **00-concepts** | token-cost-latency | `00-concepts/token-cost-latency/` | ✅ done | |
| **00-concepts** | vector-databases | `00-concepts/vector-databases/` | ✅ done | |
| **01-llm-lld-projects** | ai-safety-guardrails | `01-llm-lld-projects/ai-safety-guardrails/` | ✅ done | |
| **01-llm-lld-projects** | chunker-metadata-indexer | `01-llm-lld-projects/chunker-metadata-indexer/` | ✅ done | |
| **01-llm-lld-projects** | context-window-manager | `01-llm-lld-projects/context-window-manager/` | ✅ done | |
| **01-llm-lld-projects** | conversation-memory-store | `01-llm-lld-projects/conversation-memory-store/` | ✅ done | |
| **01-llm-lld-projects** | embedding-service | `01-llm-lld-projects/embedding-service/` | ✅ done | |
| **01-llm-lld-projects** | evaluation-harness | `01-llm-lld-projects/evaluation-harness/` | ✅ done | |
| **01-llm-lld-projects** | llm-request-orchestrator | `01-llm-lld-projects/llm-request-orchestrator/` | ✅ done | |
| **01-llm-lld-projects** | multi-agent-orchestrator | `01-llm-lld-projects/multi-agent-orchestrator/` | ✅ done | |
| **01-llm-lld-projects** | prompt-builder | `01-llm-lld-projects/prompt-builder/` | ✅ done | |
| **01-llm-lld-projects** | retriever-ranker | `01-llm-lld-projects/retriever-ranker/` | ✅ done | |
| **01-llm-lld-projects** | safety-filter-policy-engine | `01-llm-lld-projects/safety-filter-policy-engine/` | ✅ done | |
| **01-llm-lld-projects** | semantic-embedding-cache | `01-llm-lld-projects/semantic-embedding-cache/` | ✅ done | |
| **01-llm-lld-projects** | speculative-decoding-cache | `01-llm-lld-projects/speculative-decoding-cache/` | ✅ done | |
| **01-llm-lld-projects** | streaming-token-aggregator | `01-llm-lld-projects/streaming-token-aggregator/` | ✅ done | |
| **01-llm-lld-projects** | token-streaming-server | `01-llm-lld-projects/token-streaming-server/` | ✅ done | |
| **01-llm-lld-projects** | tool-router | `01-llm-lld-projects/tool-router/` | ✅ done | |
| **01-llm-lld-projects** | vector-store-inverted-index | `01-llm-lld-projects/vector-store-inverted-index/` | ✅ done | |
| **02-llm-hld-projects** | agentic-workflow-orchestrator | `02-llm-hld-projects/agentic-workflow-orchestrator/` | ✅ done | |
| **02-llm-hld-projects** | ai-coding-copilot | `02-llm-hld-projects/ai-coding-copilot/` | ✅ done | |
| **02-llm-hld-projects** | document-qa-rag | `02-llm-hld-projects/document-qa-rag/` | ✅ done | |
| **02-llm-hld-projects** | fine-tuning-pipeline | `02-llm-hld-projects/fine-tuning-pipeline/` | ✅ done | |
| **02-llm-hld-projects** | inference-serving-platform | `02-llm-hld-projects/inference-serving-platform/` | ✅ done | |
| **02-llm-hld-projects** | llm-eval-benchmark-platform | `02-llm-hld-projects/llm-eval-benchmark-platform/` | ✅ done | |
| **02-llm-hld-projects** | llm-evaluation-safety-platform | `02-llm-hld-projects/llm-evaluation-safety-platform/` | ✅ done | |
| **02-llm-hld-projects** | llm-inference-serving-engine | `02-llm-hld-projects/llm-inference-serving-engine/` | ✅ done | |
| **02-llm-hld-projects** | llm-safety-eval-platform | `02-llm-hld-projects/llm-safety-eval-platform/` | ✅ done | |
| **02-llm-hld-projects** | multi-tenant-chat-assistant | `02-llm-hld-projects/multi-tenant-chat-assistant/` | ✅ done | |
| **02-llm-hld-projects** | multi-tenant-enterprise-rag | `02-llm-hld-projects/multi-tenant-enterprise-rag/` | ✅ done | |
| **02-llm-hld-projects** | recommendation-feature-store | `02-llm-hld-projects/recommendation-feature-store/` | ✅ done | |
| **02-llm-hld-projects** | semantic-retrieval-platform | `02-llm-hld-projects/semantic-retrieval-platform/` | ✅ done | |
| **02-llm-hld-projects** | text-to-sql-assistant | `02-llm-hld-projects/text-to-sql-assistant/` | ✅ done | |
| **02-llm-hld-projects** | voice-assistant | `02-llm-hld-projects/voice-assistant/` | ✅ done | |
| **Framework docs** | GENAI-SD-FRAMEWORK.md | `GENAI-SD-FRAMEWORK.md` | ✅ done | |
| **Framework docs** | CLASSIC-VS-GENAI.md | `CLASSIC-VS-GENAI.md` | ✅ done | |
| **Framework docs** | PITFALLS.md | `PITFALLS.md` | ✅ done | |

---

## 2025-26 Staff-Level Gaps

| Task | Title | Path | Status |
|---|---|---|---|
| GENAI-001 | GENAI-001 — Register `semantic-retrieval-platform` in all indexes | TBD | 🔜 |
| GENAI-002 | GENAI-002 — Expand `semantic-retrieval-platform` to HLD-template parity | TBD | 🔜 |
| GENAI-003 | GENAI-003 — Fix GAP-LIST truthfulness, empty `diagrams/`, duplicate eval HLDs | TBD | 🔜 |
| GENAI-004 | GENAI-004 — Add inline Mermaid diagrams to all 11 concept docs | TBD | 🔜 |
| GENAI-005 | GENAI-005 — Deepen RAG architecture to staff level | TBD | 🔜 |
| GENAI-006 | GENAI-006 — New concept: LLM inference serving | TBD | 🔜 |
| GENAI-007 | GENAI-007 — New concept: agents, MCP/A2A and memory architectures | TBD | 🔜 |
| GENAI-008 | GENAI-008 — New concept: fine-tuning vs RAG vs prompting | TBD | 🔜 |
| GENAI-009 | GENAI-009 — Deepen guardrails and prompt-injection security | TBD | 🔜 |
| GENAI-010 | GENAI-010 — New concept: LLMOps, observability, multi-tenancy and cost budgets | TBD | 🔜 |
| GENAI-011 | GENAI-011 — New HLD: LLM inference serving platform | TBD | 🔜 |
| GENAI-012 | GENAI-012 — New HLD: fine-tuning / model-training pipeline | TBD | 🔜 |
| GENAI-013 | GENAI-013 — New HLD: AI search engine (Perplexity-like) | TBD | 🔜 |
| GENAI-014 | GENAI-014 — New HLD: text-to-SQL / analytics assistant | TBD | 🔜 |
| GENAI-015 | GENAI-015 — New HLD: guardrails / AI gateway | TBD | 🔜 |
| GENAI-016 | GENAI-016 — New HLD: recommendation system with feature store | TBD | 🔜 |
| GENAI-017 | GENAI-017 — New HLD: image/video generation service | TBD | 🔜 |
| GENAI-018 | GENAI-018 — New HLD: real-time voice assistant | TBD | 🔜 |
| GENAI-019 | GENAI-019 — New HLD: GPU cluster scheduling for AI workloads | TBD | 🔜 |
| GENAI-020 | GENAI-020 — Add semantic-cache and token-budget LLD projects | TBD | 🔜 |
| GENAI-021 | GENAI-021 — Add `v2-extended` tracks to key LLD projects | TBD | 🔜 |
| GENAI-022 | GENAI-022 — Document how to run GenAI tests and add an aggregate runner | TBD | 🔜 |
| GENAI-023 | GENAI-023 — Add INTERVIEW-QA / INTERVIEW-GUIDE to every concept and HLD | TBD | 🔜 |

## Summary

| Subsection | Total | ✅ Done | 🔜 Missing | ⚠️ Incomplete |
|---|---|---|---|---|
| 00-concepts | 18 | 18 | 0 | 0 |
| 01-llm-lld-projects | 17 | 17 | 0 | 0 |
| 02-llm-hld-projects | 15 | 15 | 0 | 0 |
| Framework docs | 3 | 3 | 0 | 0 |
| **Total** | **53** | **53** | **0** | **0** |

## Completed This Session

1. ✅ **embedding-service** — Full LLD project with PROBLEM.md, DESIGN.md, APPROACH.md, v1-basic Python implementation (43 tests passing)
2. ✅ **tool-router** — Full LLD project with PROBLEM.md, DESIGN.md, APPROACH.md, v1-basic Python implementation (57 tests passing)
3. ✅ **evaluation-harness** — Full LLD project with PROBLEM.md, DESIGN.md, APPROACH.md, v1-basic Python implementation (63 tests passing)
4. ✅ **llm-safety-eval-platform** — APPROACH.md expanded from 91 to 775 lines
