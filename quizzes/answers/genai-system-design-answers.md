# GenAI System Design Quiz - Answer Key

## Answers

| # | Answer | Explanation |
|---|--------|-------------|
| 1 | B | RAG is an evidence pipeline: index, retrieve, rerank, assemble context, generate, and evaluate grounding. |
| 2 | B | The indexing pipeline decides which parsed, chunked, embedded, and stored knowledge can later be retrieved. |
| 3 | B | Chunk size and overlap shape whether retrieval returns coherent but noisy context or precise but fragmented context. |
| 4 | A | Initial retrieval favors recall; reranking improves precision on the candidate set before the LLM sees context. |
| 5 | C | Unauthorized chunks must never enter the prompt because the model could expose them in the answer. |
| 6 | B | Structured facts often need SQL or API lookup rather than vector similarity alone. |
| 7 | C | Citations/source snippets tie generated claims back to retrieved evidence. |
| 8 | A | Indirect injection can arrive through retrieved documents, so retrieved context needs scanning and constraints. |
| 9 | A | A high-quality answer is not shippable if it violates safety, privacy, or policy requirements. |
| 10 | A | Attack success rate is the share of adversarial attempts that bypass safety controls. |
| 11 | C | Robust evaluation combines controlled regression checks with production monitoring, attacks, and human audit slices. |
| 12 | B | Versioned golden sets preserve apples-to-apples regression tracking across prompts, models, and policies. |
| 13 | B | LLM judges can show verbosity, position, self-preference, and score-drift biases, so they need calibration. |
| 14 | B | Full decision lineage supports debugging, rollback, governance, and post-incident attribution. |
| 15 | B | Routing matches each request to the right quality/cost/latency tier. |
| 16 | B | Cascading starts cheap and escalates only when confidence, validation, or policy signals require it. |
| 17 | A | Per-route quality, escalation, latency, and cost trends reveal misrouting and drift. |
| 18 | B | Time to first token captures perceived latency for streamed LLM responses. |
| 19 | B | Stable interview reasoning estimates tokens, traffic, model tiers, and optimization levers instead of relying on live prices. |
| 20 | A | Semantic caching can save cost and latency but needs freshness, invalidation, and tenant/policy controls. |
| 21 | B | The model emits structured tool requests; application code authorizes and executes them. |
| 22 | A | Agent loops can retry or replay, so write tools need deduplication or confirmation to avoid duplicate side effects. |
| 23 | A | Agents are justified when the system needs plan-act-observe loops and tool-backed adaptation. |
| 24 | A | Iteration and timeout limits contain runaway cost, latency, and side effects. |
| 25 | B | High-impact actions require a constrained registry, validation, authorization, policy checks, and auditability. |
| 26 | A | Durable execution preserves state so long-running agent tasks can resume and be audited after failures. |
| 27 | A | Prompt Builder owns prompt construction, safe interpolation, and token budget guarding. |
| 28 | B | Retriever & Ranker owns retrieval strategies and ranking/reranking behavior. |
| 29 | A | Caching embeddings avoids recomputing vectors for repeated normalized inputs. |
| 30 | A | Safety Filter & Policy Engine maps content signals to thresholds and enforcement actions. |
| 31 | A | Evaluation Harness runs test cases and computes repeatable quality/safety metrics. |
| 32 | A | Document Q&A RAG depends on the full ingestion-to-citation retrieval pipeline. |
| 33 | B | Multi-tenant assistants must isolate data, memory, policies, budgets, and SLA-sensitive routing. |
| 34 | A | Copilots need low-latency completions and richer reasoning/chat paths with different budgets. |
| 35 | A | Eval/safety platforms collect evidence, score quality/safety, report issues, and gate releases. |
| 36 | A | Retrieval serving must be fast, relevant, permission-aware, and observable for downstream RAG quality. |
