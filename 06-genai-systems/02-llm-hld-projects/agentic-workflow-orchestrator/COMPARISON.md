# Agentic Workflow Orchestrator — Comparison

## Agentic Workflow vs Standard Chatbot

| Concern | Agentic Workflow Orchestrator | Standard Chatbot |
|---|---|---|
| Interaction mode | Stateful, multi-step actions and execution | Single-turn or conversational text generation |
| Side effects | Designed for real-world changes (APIs, databases) | Typically read-only or scoped to conversational state |
| Autonomy | High (plans and executes multiple steps automatically) | Low (awaits user input for each step) |
| Core engine | Orchestration loop + tool execution engine | Simple stateless generation or basic RAG retrieval |

## Agentic Workflow vs Traditional Workflow Engines (e.g., Temporal, Airflow)

| Concern | Agentic Workflow Orchestrator | Traditional Workflow Engines |
|---|---|---|
| Control flow | Dynamic, planned by LLM based on intent and results | Static, pre-defined DAGs or code-based logic |
| Error handling | Semantic recovery (LLM re-plans if tool fails) | Code-driven retries and explicit failure paths |
| Input format | Unstructured natural language intent | Structured data/payloads and API triggers |
| Human-in-the-loop | Dynamic approval gates based on action risk | Pre-defined manual approval steps in the DAG |

## Agentic Workflow vs Robotic Process Automation (RPA)

| Concern | Agentic Workflow Orchestrator | Robotic Process Automation |
|---|---|---|
| Interface | API-first with semantic tool calling | Screen scraping and UI automation |
| Adaptability | High (tolerates minor API or format changes) | Low (brittle to UI or layout changes) |
| Logic type | Non-deterministic, semantic reasoning | Deterministic, rule-based execution |
| Maintenance | Updating tool schemas and prompt guardrails | Re-recording scripts and selectors |
