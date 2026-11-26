# GenAI System Design Flashcards

60 question-only flashcards for GenAI system design interview preparation.

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

## RAG and Retrieval Quality (12 Cards)

### Card 1
Front: What makes RAG an evidence pipeline rather than just a vector database plus an LLM?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality. Scaling vector databases requires efficient indexing (like HNSW) to maintain low-latency similarity search over millions of embeddings.

Back: Scaling vector databases requires efficient indexing algorithms (like HNSW or IVF) and distributed architectures to handle high-throughput similarity searches over millions of vectors.

### Card 2
Front: Which decisions belong in the offline indexing path of a RAG system?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: Retrieval-Augmented Generation (RAG) grounds the LLM by retrieving relevant facts from a knowledge base, reducing hallucinations and allowing the model to answer queries based on private data.

### Card 3
Front: How do chunk size and overlap affect retrieval precision and context coherence?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'overlap', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 4
Front: When should you choose hybrid retrieval over vector-only retrieval?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality. Scaling vector databases requires efficient indexing (like HNSW) to maintain low-latency similarity search over millions of embeddings.

Back: Scaling vector databases requires efficient indexing algorithms (like HNSW or IVF) and distributed architectures to handle high-throughput similarity searches over millions of vectors.

### Card 5
Front: Why does a reranker improve a high-stakes RAG answer?

Back: This approach is necessary to mitigate hallucinations and ground the model's responses in factual, private data. It also directly impacts the overall latency and cost of the system.

Back: Retrieval-Augmented Generation (RAG) grounds the LLM by retrieving relevant facts from a knowledge base, reducing hallucinations and allowing the model to answer queries based on private data.

### Card 6
Front: What metadata should travel with each chunk so retrieval remains explainable and controllable?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'explainable', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 7
Front: Where should ACL filtering happen in a permission-aware RAG pipeline?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: Retrieval-Augmented Generation (RAG) grounds the LLM by retrieving relevant facts from a knowledge base, reducing hallucinations and allowing the model to answer queries based on private data.

### Card 8
Front: How do citations change the trust model for a document Q&A assistant?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'trust', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 9
Front: What failure mode does lost-in-the-middle mitigation address?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'lost-in-the-middle', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 10
Front: How would you evaluate retrieval recall separately from final answer quality?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'recall', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 11
Front: When is iterative retrieval justified instead of a single top-k search?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'top-k', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 12
Front: What is the minimum RAG pipeline you should draw in a system design interview?

Back: In GenAI architecture, minimum is responsible for managing context limits and ensuring generation quality. It is a core part of scaling LLM applications in production.

Back: Retrieval-Augmented Generation (RAG) grounds the LLM by retrieving relevant facts from a knowledge base, reducing hallucinations and allowing the model to answer queries based on private data.

---

## Safety, Evaluation, and Governance (12 Cards)

### Card 13
Front: What are the main attack surfaces in an LLM application?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'application', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 14
Front: How does indirect prompt injection enter a RAG system?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: Retrieval-Augmented Generation (RAG) grounds the LLM by retrieving relevant facts from a knowledge base, reducing hallucinations and allowing the model to answer queries based on private data.

### Card 15
Front: Why should system prompts never contain secrets?

Back: This approach is necessary to mitigate hallucinations and ground the model's responses in factual, private data. It also directly impacts the overall latency and cost of the system.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'should', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 16
Front: What is the difference between input guardrails and output guardrails?

Back: In GenAI architecture, difference is responsible for managing context limits and ensuring generation quality. It is a core part of scaling LLM applications in production.

Back: Guardrails in GenAI systems are implemented via input/output filtering, using smaller secondary models to detect toxicity, PII, or off-topic responses before they reach the user.

### Card 17
Front: What makes safety a hard release gate instead of an average-quality metric?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: Retrieval-Augmented Generation (RAG) grounds the LLM by retrieving relevant facts from a knowledge base, reducing hallucinations and allowing the model to answer queries based on private data.

### Card 18
Front: How do you define attack success rate for a red-team suite?

Back: You handle this by implementing robust orchestration patterns like RAG (Retrieval-Augmented Generation) or agentic routing. This involves tuning hyperparameters and carefully managing the token budget during API calls.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'define', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 19
Front: What categories should a golden set cover for a GenAI system?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'system', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 20
Front: Why should golden sets be versioned?

Back: This approach is necessary to mitigate hallucinations and ground the model's responses in factual, private data. It also directly impacts the overall latency and cost of the system.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'should', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 21
Front: What biases can affect LLM-as-judge evaluation?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'biases', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 22
Front: How do offline evaluation and online monitoring complement each other?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'other', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 23
Front: What event fields are required for GenAI auditability?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'auditability', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 24
Front: How would you combine faithfulness, relevance, safety pass rate, and user feedback into release decisions?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'faithfulness,', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

## Model Routing, Cost, and Latency (10 Cards)

### Card 25
Front: What request properties should a model router consider?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'properties', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 26
Front: How does cascading routing reduce cost while preserving quality?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'quality', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 27
Front: What confidence signals can trigger escalation to a stronger model?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'trigger', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 28
Front: What metrics reveal that a router is misclassifying hard requests?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'metrics', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 29
Front: How do you estimate token cost for a new GenAI feature without relying on exact vendor prices?

Back: You handle this by implementing robust orchestration patterns like RAG (Retrieval-Augmented Generation) or agentic routing. This involves tuning hyperparameters and carefully managing the token budget during API calls. Token budgeting prevents exceeding context windows and controls inference costs, often requiring aggressive chunking or summarization.

Back: Token budgeting is essential to avoid exceeding the context window and to manage API costs. Techniques include summarizing chat history and aggressively filtering retrieved documents.

### Card 30
Front: What is the difference between time to first token and total completion latency?

Back: In GenAI architecture, difference is responsible for managing context limits and ensuring generation quality. It is a core part of scaling LLM applications in production. Token budgeting prevents exceeding context windows and controls inference costs, often requiring aggressive chunking or summarization.

Back: Token budgeting is essential to avoid exceeding the context window and to manage API costs. Techniques include summarizing chat history and aggressively filtering retrieved documents.

### Card 31
Front: Why does streaming improve perceived latency but complicate output safety checks?

Back: This approach is necessary to mitigate hallucinations and ground the model's responses in factual, private data. It also directly impacts the overall latency and cost of the system.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'improve', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 32
Front: When is semantic caching useful, and what risks does it introduce?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'introduce', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 33
Front: What belongs in a latency waterfall for a RAG answer?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: Retrieval-Augmented Generation (RAG) grounds the LLM by retrieving relevant facts from a knowledge base, reducing hallucinations and allowing the model to answer queries based on private data.

### Card 34
Front: How do prompt compression, output limits, caching, and routing attack different parts of the cost problem?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'output', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

## Agents and Tool Use (10 Cards)

### Card 35
Front: What does the client/orchestrator own in a tool-calling flow?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'client/orchestrator', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 36
Front: Why is tool schema validation not enough for high-impact actions?

Back: This approach is necessary to mitigate hallucinations and ground the model's responses in factual, private data. It also directly impacts the overall latency and cost of the system.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'actions', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 37
Front: How do you decide between simple RAG and an agent loop?

Back: You handle this by implementing robust orchestration patterns like RAG (Retrieval-Augmented Generation) or agentic routing. This involves tuning hyperparameters and carefully managing the token budget during API calls.

Back: Retrieval-Augmented Generation (RAG) grounds the LLM by retrieving relevant facts from a knowledge base, reducing hallucinations and allowing the model to answer queries based on private data.

### Card 38
Front: What is the ReAct loop in system-design terms?

Back: In GenAI architecture, react is responsible for managing context limits and ensuring generation quality. It is a core part of scaling LLM applications in production.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'terms', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 39
Front: Why do agent tools need idempotency keys or confirmation gates?

Back: This approach is necessary to mitigate hallucinations and ground the model's responses in factual, private data. It also directly impacts the overall latency and cost of the system.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'tools', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 40
Front: What max-iteration, timeout, and budget controls should every production agent have?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'should', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 41
Front: How should a tool registry constrain what an LLM can request?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'request', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 42
Front: What should be logged for every tool call in an agent workflow?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'should', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 43
Front: When should a human-in-the-loop checkpoint interrupt an agent?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'human-in-the-loop', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 44
Front: What makes durable execution important for long-running agent tasks?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'makes', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

## GenAI LLD Components (8 Cards)

### Card 45
Front: What responsibilities belong in a Chunker & Metadata Indexer?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'responsibilities', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 46
Front: What interface boundaries should a Retriever & Ranker expose?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'interface', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 47
Front: How should a Prompt Builder enforce token budgets and safe interpolation?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality. Token budgeting prevents exceeding context windows and controls inference costs, often requiring aggressive chunking or summarization.

Back: Token budgeting is essential to avoid exceeding the context window and to manage API costs. Techniques include summarizing chat history and aggressively filtering retrieved documents.

### Card 48
Front: What memory strategies should a Conversation Memory Store support?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'memory', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 49
Front: What policy decisions should a Safety Filter & Policy Engine own outside the model?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'model', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 50
Front: Which retry, backoff, circuit-breaker, and observability concerns belong in an LLM Request Orchestrator?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'belong', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 51
Front: What should an Embedding Service cache and normalize?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'should', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 52
Front: How should an Evaluation Harness separate test cases, model adapters, metrics, and reports?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'metrics,', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

## HLD Scenario Drills (8 Cards)

### Card 53
Front: How would you design the end-to-end flow for Document Q&A with cited RAG answers?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: Retrieval-Augmented Generation (RAG) grounds the LLM by retrieving relevant facts from a knowledge base, reducing hallucinations and allowing the model to answer queries based on private data.

### Card 54
Front: What tenant-isolation boundaries matter in a multi-tenant chat assistant?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'tenant-isolation', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 55
Front: Why does an AI coding copilot need separate fast-completion and rich-chat paths?

Back: This approach is necessary to mitigate hallucinations and ground the model's responses in factual, private data. It also directly impacts the overall latency and cost of the system.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'paths', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 56
Front: What components define an agentic workflow orchestrator for multi-step tasks?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'orchestrator', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 57
Front: How would you design a central LLM evaluation and safety platform?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'central', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

### Card 58
Front: What makes a governance-focused safety/eval platform different from an app-local guardrail layer?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: Guardrails in GenAI systems are implemented via input/output filtering, using smaller secondary models to detect toxicity, PII, or off-topic responses before they reach the user.

### Card 59
Front: How would you serve a low-latency semantic retrieval platform for many RAG applications?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: Retrieval-Augmented Generation (RAG) grounds the LLM by retrieving relevant facts from a knowledge base, reducing hallucinations and allowing the model to answer queries based on private data.

### Card 60
Front: What five GenAI-specific sections should appear in every full HLD answer?

Back: The architecture must balance retrieval latency with the semantic richness of the context provided to the LLM. Continuous evaluation (e.g., LLM-as-a-judge) is required to monitor output quality.

Back: GenAI system design involves orchestrating LLMs, managing context windows, and ensuring low-latency retrieval while mitigating risks like hallucinations and prompt injection. Specifically, regarding 'appear', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.
