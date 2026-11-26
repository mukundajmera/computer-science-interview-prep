# Approach: AI Safety Guardrails Engine

## 1. Pipeline Architecture

The AI Safety Guardrails engine is designed as a **Chain of Responsibility** / **Pipeline** pattern, separated into two distinct phases:
1. **Pre-Execution Pipeline**: Validates, sanitizes, and potentially rejects the raw user input before it is sent to the LLM.
2. **Post-Execution Pipeline**: Evaluates the LLM's generated response for toxicity, policy violations, and hallucination against a source context before it reaches the user.

This decoupling ensures that safety concerns are strictly isolated from core business logic or LLM inference loops.

## 2. Injected Interfaces over Concrete Dependencies

To remain provider-agnostic and ensure the component is a standalone micro-unit, the design heavily utilizes **Dependency Injection** via model/provider-independent interfaces.
- **Model Independence**: The engine does not make network calls to OpenAI, Anthropic, or HuggingFace. Any semantic operations (like toxicity classification or embedding-based hallucination checking) rely on injected functional interfaces (e.g., `Callable[[str], float]`).
- **Standard Library Approximations**: For educational purposes, complex NLP tasks are approximated using standard library tools. PII detection utilizes regex; Prompt Injection relies on heuristic substring and regex matching (e.g., matching "ignore all previous instructions").

## 3. Execution Flow and Fast-Failing

The pipeline is designed to **fail fast**. Guardrails are evaluated sequentially.
- If a guardrail returns a `Block` action, the entire pipeline immediately halts, returning the violation rationale to the caller. This saves computation and prevents downstream components (or expensive LLM calls) from processing malicious input.
- If a guardrail returns a `Redact` (Modify) action, the modified text is passed to the next guardrail in the chain.

## 4. Privacy and Tenant Isolation

In enterprise environments, guardrails must not leak data across tenants or concurrent requests.
- **Stateless Guardrails**: Individual guardrails (`PIIRedactor`, `PromptInjectionDetector`) are designed to be stateless and immutable after initialization. They do not store request-specific information in instance variables.
- **Context Objects**: Request context (such as tenant IDs, RAG source documents, and metadata) is encapsulated in a dedicated `ValidationContext` object passed through the pipeline, tested via explicit normal/error/cancellation/privacy fixtures.

## 5. Extensibility (Open/Closed Principle)

The engine itself (`GuardrailsEngine`) is closed for modification but open for extension.
- Adding a new guardrail (e.g., a custom regex filter for internal company codes) simply requires implementing the `Guardrail` interface (specifically `PreExecutionGuardrail` or `PostExecutionGuardrail`) and appending it to the engine's list during initialization. No core logic in `GuardrailsEngine` needs to change.

## 6. Trade-offs and Limitations

- **Heuristic vs. Semantic Security**: Relying on regex for Prompt Injection is fundamentally brittle against sophisticated adversarial attacks (jailbreaks). Real-world implementations require dedicated secondary LLMs or specialized classification models. Our design supports injecting these advanced models via interfaces, but defaults to heuristics for the baseline implementation.
- **Synchronous Execution**: The initial design evaluates guardrails synchronously. While easier to debug and trace, this can introduce latency. A production system might parallelize non-mutating guardrails (e.g., running toxicity and hallucination checks concurrently).
