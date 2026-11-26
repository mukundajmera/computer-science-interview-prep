# GenAI System Design Quiz

36 questions focused on GenAI system design interviews: RAG, safety and evaluation, routing, token cost and latency, agents/tool use, GenAI LLD components, and HLD scenario drills.

Time: 50 minutes  
Difficulty: Hard

Source alignment:
- [GenAI SD Framework](../06-genai-systems/GENAI-SD-FRAMEWORK.md)
- [RAG Architecture](../06-genai-systems/00-concepts/rag-architecture/)
- [Model Routing & Orchestration](../06-genai-systems/00-concepts/model-routing-orchestration/)
- [Token Economics](../06-genai-systems/00-concepts/token-cost-latency/)
- [Prompting, Tools & Agents](../06-genai-systems/00-concepts/prompting-tools-agents/)
- [Safety, Evaluation & Governance](../06-genai-systems/00-concepts/safety-eval/)
- [GenAI LLD Projects](../06-genai-systems/01-llm-lld-projects/)
- [GenAI HLD Projects](../06-genai-systems/02-llm-hld-projects/)

---

## Section 1: RAG and Retrieval Quality (7)

### Question 1
In a GenAI system design interview, what is the strongest mental model for RAG?

A) A vector database attached to an LLM  
B) An evidence pipeline from indexing to retrieval to grounded generation  
C) A fine-tuning replacement for every domain task  
D) A cache for model outputs only

### Question 2
Which stage most directly determines what knowledge is searchable before a user query arrives?

A) Output filtering  
B) Indexing pipeline  
C) Model router  
D) Human review queue

### Question 3
Why is chunk size a first-class RAG design decision?

A) It changes the frontend rendering framework  
B) It controls the precision/coherence trade-off of retrieved context  
C) It eliminates the need for embeddings  
D) It guarantees no hallucinations

### Question 4
What is the best reason to add a reranker after initial retrieval?

A) To optimize precision on a smaller candidate set before prompt assembly  
B) To avoid storing metadata  
C) To make all queries deterministic  
D) To replace access control checks

### Question 5
A permission-aware enterprise RAG system must apply authorization:

A) only after the LLM produces an answer  
B) only during nightly ingestion  
C) before retrieved chunks can enter the prompt context  
D) only in the browser

### Question 6
Which routing choice fits a structured data question in a RAG-like assistant?

A) Always vector search  
B) SQL/API lookup path when the question needs structured facts  
C) Reranking only, no retrieval  
D) Output toxicity classifier

### Question 7
What is the strongest grounding signal for a document Q&A answer?

A) A longer answer  
B) Higher model temperature  
C) Citations or source snippets tied to retrieved evidence  
D) More retries

---

## Section 2: Safety, Evaluation, and Governance (7)

### Question 8
Which safety layer addresses indirect prompt injection in RAG?

A) Scan and constrain retrieved document context before prompt assembly  
B) Increase output length  
C) Use only round-robin model routing  
D) Disable indexing metadata

### Question 9
Why should safety act as a hard deploy gate rather than a soft quality metric?

A) Safety failures can create unacceptable harm even when answer quality is high  
B) Safety metrics are always cheaper than latency metrics  
C) Safety replaces all online monitoring  
D) Safety only matters for batch jobs

### Question 10
What does attack success rate measure?

A) Fraction of adversarial inputs that bypass guardrails  
B) Average time to first token  
C) Percentage of cache hits  
D) Number of indexed chunks per tenant

### Question 11
Which evaluation stack is strongest for GenAI systems?

A) Offline golden sets only  
B) Online thumbs-up/down only  
C) Offline gates, online monitoring, adversarial tests, and sampled human review  
D) Unit tests for API schemas only

### Question 12
Why version golden sets instead of mutating them in place?

A) To make prompt files shorter  
B) To preserve regression comparability across model and prompt changes  
C) To remove the need for metadata  
D) To reduce vector index size

### Question 13
What is a key risk of LLM-as-judge evaluation?

A) Judges cannot return text  
B) Biases such as verbosity, position, self-preference, and calibration drift  
C) It cannot be batched  
D) It only works for latency metrics

### Question 14
Which event data best supports post-incident auditability?

A) User agent string only  
B) Prompt, retrieved sources, model version, policy version, tool calls, and safety outcomes  
C) CSS class names  
D) Only the final answer text

---

## Section 3: Model Routing, Cost, and Latency (6)

### Question 15
What is the main reason to introduce model routing?

A) Every model has identical cost and latency  
B) Different requests have different quality, cost, and latency needs  
C) It removes the need for evaluation  
D) It guarantees no provider outage

### Question 16
How does a cascading router usually optimize spend?

A) It always starts with the largest model  
B) It starts with a cheaper path and escalates on low confidence or validation failure  
C) It runs every model in parallel  
D) It disables fallback handling

### Question 17
Which signal is most useful for catching router drift?

A) Per-route quality, escalation, latency, and cost metrics over time  
B) Number of Markdown headings  
C) Browser viewport width  
D) Repository file count

### Question 18
Which latency metric best explains when a user first sees streamed output?

A) Total monthly cost  
B) Time to first token  
C) Number of embedding dimensions  
D) Golden set size

### Question 19
What is the safest way to discuss token economics in an interview?

A) Ignore it until implementation  
B) Estimate input tokens, output tokens, traffic, model tier, and caching/routing levers  
C) Quote exact vendor prices from memory  
D) Claim all GenAI calls are negligible cost

### Question 20
Which trade-off is introduced by semantic caching?

A) Faster and cheaper repeated answers, with freshness and cache-governance risk  
B) Higher latency with no cost benefit  
C) Better authorization by default  
D) Guaranteed answer correctness

---

## Section 4: Agents and Tool Use (6)

### Question 21
In tool calling, who executes the tool?

A) The model directly mutates external systems  
B) The client/orchestrator executes approved tool calls emitted by the model  
C) The vector database executes every tool  
D) The browser executes hidden server tools

### Question 22
Why should write-capable agent tools use idempotency keys or confirmation gates?

A) Agent loops may retry or replay tool calls  
B) It improves tokenization quality  
C) It replaces authorization  
D) It removes the need for logs

### Question 23
When is an agent loop more justified than simple RAG?

A) The task requires multi-step planning, tool execution, observation, and adaptation  
B) The task is a single factual lookup  
C) The answer must always be one sentence  
D) The corpus is static and small

### Question 24
What is the purpose of max-iteration and timeout guards in agent execution?

A) Prevent runaway loops and unbounded cost or side effects  
B) Improve Markdown rendering  
C) Increase context length  
D) Disable tool observability

### Question 25
Which tool-routing design is safest for high-impact actions?

A) Let the model call any endpoint by name  
B) Approved registry, schema validation, authorization, and action-specific policy checks  
C) Store credentials in the system prompt  
D) Skip audit logs for speed

### Question 26
What is the primary benefit of durable execution in an agentic workflow orchestrator?

A) It can resume, audit, and control long-running task state across failures  
B) It removes all human review  
C) It avoids all model calls  
D) It makes tools non-idempotent

---

## Section 5: GenAI LLD Components (5)

### Question 27
Which LLD component owns prompt template assembly and budget guarding?

A) Prompt Builder  
B) Retriever & Ranker  
C) Safety Filter only  
D) Vector database

### Question 28
Which component best fits dense/sparse/hybrid retrieval with pluggable ranking?

A) Conversation Memory Store  
B) Retriever & Ranker  
C) Tool Router  
D) Evaluation Harness

### Question 29
What should an embedding service cache?

A) Reusable embedding results for identical or normalized inputs  
B) Raw user passwords  
C) Final browser HTML  
D) All rejected safety prompts forever

### Question 30
Which component should evaluate rules, categories, thresholds, and resulting moderation actions?

A) Safety Filter & Policy Engine  
B) Chunker only  
C) Model cost calculator only  
D) Static site generator

### Question 31
What is the main purpose of an evaluation harness LLD component?

A) Run test cases against model/system outputs and compute metrics consistently  
B) Serve CSS files  
C) Replace all human judgment  
D) Store tenant billing data only

---

## Section 6: HLD Scenario Drills (5)

### Question 32
For Document Q&A RAG, which architecture path is most central?

A) Ingest -> chunk -> embed -> retrieve -> rerank -> generate with citations  
B) User -> model only -> no storage  
C) Browser -> CSS -> answer  
D) Random sample -> no prompt context

### Question 33
For a multi-tenant chat assistant, what must be isolated per tenant?

A) Only button colors  
B) Data, memory, safety policy, usage budgets, and often routing/SLA controls  
C) Only the model name in logs  
D) Nothing if prompts are short

### Question 34
For an AI coding copilot, why use a dual-path fast+rich design?

A) Fast completions and deeper chat/reasoning have different latency and context needs  
B) It avoids context engineering  
C) It makes safety unnecessary  
D) It removes evaluation from the system

### Question 35
For an LLM evaluation and safety platform, which pipeline is most important?

A) Collect traces/test cases -> run evals/red-team suites -> score -> report/alert -> gate releases  
B) Generate UI themes -> deploy frontend  
C) Delete logs -> reduce storage  
D) Always accept model outputs

### Question 36
For a semantic retrieval platform used by RAG apps, what is the most important serving constraint?

A) Low-latency, high-relevance retrieval that respects metadata and ACL filtering  
B) Highest possible output token count  
C) No index lifecycle management  
D) No observability
