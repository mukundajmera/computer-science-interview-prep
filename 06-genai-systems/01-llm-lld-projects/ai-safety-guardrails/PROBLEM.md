# AI Safety Guardrails Engine

## 1. 📚 Topic Level & Prerequisites
- **Layering:** Core (Standard interview readiness, focusing on architecture and standard interfaces)
- **Prerequisites:** Basic understanding of LLM pipelines and RAG architectures.

## Problem Statement

Design an AI Safety Guardrails microcomponent that intercepts, evaluates, and potentially modifies or blocks interactions between user inputs and a Large Language Model (LLM). The system acts as a multi-stage pipeline with two distinct phases: pre-execution (validating/redacting user prompts before sending them to the LLM) and post-execution (validating the LLM's response before returning it to the user). The component must be extensible, pluggable, and fully decoupled from any specific LLM provider or transport layer.

---

## Functional Requirements

1. **Multi-Stage Pipeline**: Support distinct Pre-Execution and Post-Execution guardrail hooks.
2. **PII Redaction (Regex/Rule-based)**: Detect and redact sensitive information (SSN, credit cards, emails, phone numbers) before it reaches the LLM model.
3. **Prompt Injection Detection**: Intercept malicious inputs via heuristic detection (evaluating canary tokens, system prompt overrides, and roleplay escapes).
4. **Toxicity Classification Stub**: Evaluate the toxicity of user inputs and model outputs, returning a confidence score to block severe violations.
5. **Hallucination Grounding Checker**: Check the generated LLM response claims against a provided source context (e.g., in a RAG application) to prevent ungrounded hallucinations.
6. **Pass-Through**: Allow clean input and output to pass through unmodified with minimal overhead.
7. **Action Types**: Guardrails can take actions such as `Allow`, `Redact` (modify), or `Block` (halt pipeline).
8. **Pluggable Architecture**: Allow new guardrails to be dynamically added or removed without altering the core engine.

---

## Non-Functional Requirements

1. **Model & Provider Independence**: The guardrails engine must not rely on proprietary API clients. Interfaces for models, tokenizers, and embeddings must be injected.
2. **Deterministic Evaluation**: Given the same input, configuration, and source context, the pipeline must produce identical decisions and actions.
3. **Tenant & Privacy Isolation**: Ensure state and cached evaluations do not leak across concurrent requests or different tenants.
4. **Extensibility**: Follow the Open/Closed principle to support custom customer-defined guardrails.
5. **Standard Library Only**: Built entirely using Python's standard library (e.g., `re`, `typing`, `collections`). No dependencies on LangChain, NeMo Guardrails, or proprietary NLP libraries.

---

## Scope & Non-Goals

- **In Scope**: A single microcomponent with explicit normal/error/cancellation/privacy fixtures and model/provider-independent interfaces.
- **Non-Goals / Constraints**: 
  - **Simulation/Stubbing**: This is a standalone, educational microcomponent. Any toxicity classifier or hallucination checking relies on heuristic stubs or injected mocks rather than real machine learning models.
  - **No Production Guarantees**: This implementation does **not** provide production-grade safety, adversarial robustness, real tokenization, or genuine vector embedding capabilities. It approximates these mechanisms for architectural study.
  - **Synchronous Execution**: The v1 pipeline will execute guardrails synchronously and sequentially.
  - **String Processing**: Inputs and outputs are treated as plain UTF-8 text strings.

---

## Sample Interactions

```
1. Caller initializes GuardrailsEngine with a list of Pre and Post guardrails.
2. Caller submits a request: "My email is user@example.com. Ignore all previous instructions."
3. Engine triggers Pre-Execution Pipeline.
4. PIIRedactor identifies and replaces the email: "My email is [REDACTED_EMAIL]. Ignore all previous instructions."
5. PromptInjectionDetector flags "Ignore all previous instructions." and returns a Block action.
6. Engine immediately halts and returns a safety violation response to the Caller.
7. (Alternative flow) If clean, input is forwarded to the LLM by the caller.
8. Caller submits LLM response to Post-Execution Pipeline.
9. HallucinationGroundingChecker evaluates claims against source context.
10. Engine returns the final validated response to the caller.
```

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| GuardrailsEngine | Orchestrates the multi-stage validation pipeline |
| GuardrailAction | Enumeration of possible actions (Allow, Block, Redact) |
| GuardrailResult | Data object containing the action, modified text, and reasoning |
| Guardrail | Abstract interface for all specific safety checks |
| PreExecutionGuardrail | Marker interface/abstract class for pre-generation checks |
| PostExecutionGuardrail| Marker interface/abstract class for post-generation checks |
| PIIRedactor | Regex/rule-based guardrail for masking sensitive data |
| PromptInjectionDetector | Heuristic detector for canary tokens and jailbreak patterns |
| ToxicityClassifierStub | Simulated classifier to flag harmful content |
| HallucinationGroundingChecker | Compares generated text against provided source context |
| ValidationContext | Encapsulates request-scoped data to ensure tenant isolation |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Core engine, synchronous pipeline, PII redactor, heuristic injection detector, toxicity stub |
| v2-extended | Async pipeline, parallel execution, hallucination checker, custom tenant policies |
| v3-optimized| Caching, semantic similarity stubs, detailed tracing and telemetry |
