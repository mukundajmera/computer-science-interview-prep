# Prompt Builder

## Problem Statement

Design a prompt assembly system that constructs LLM prompts from multiple input sections — system instructions, user messages, retrieved context snippets, and tool outputs — while enforcing a context-length budget and providing safe variable interpolation that prevents injection attacks.

---

## Functional Requirements

1. **Section Assembly**: Compose prompts from named sections — system instructions, user messages, retrieved context snippets, and tool outputs
2. **Template Engine**: Support named placeholders (`{variable_name}`) with safe interpolation that never executes user-supplied code
3. **Context-Length Budget**: Estimate token counts using a word-based approximation and enforce a configurable maximum token budget
4. **Budget Allocation**: Assign per-section token budgets (system, context, user, tools) so that each category has a guaranteed share
5. **Priority-Based Truncation**: When the assembled prompt exceeds the budget, truncate lower-priority sections first while preserving higher-priority content
6. **Conditional Sections**: Support optional template sections that are included only when their variables are provided
7. **List Rendering**: Render list variables as formatted multi-line content within templates

---

## Non-Functional Requirements

1. **Safety**: No `eval`, `exec`, or format-string code paths that could execute user-supplied input — interpolation must be purely textual
2. **Determinism**: Given the same inputs and configuration, the builder must produce identical output every run
3. **Extensibility**: New section types and truncation strategies can be added without modifying existing classes
4. **Testability**: Every component must be independently unit-testable
5. **Standard Library Only**: No external dependencies — use Python's built-in modules exclusively

---

## Constraints & Assumptions

- Token estimation uses a simple heuristic: `token_count ≈ word_count × 1.3` (a common approximation for English text)
- The system does **not** call a real tokenizer (tiktoken, SentencePiece, etc.); callers can inject a custom estimator
- Placeholder names follow identifier rules: `[a-zA-Z_][a-zA-Z0-9_]*`
- Undefined placeholders in a template raise an error by default; a lenient mode leaves them as empty strings
- Section priorities are integers — lower number means higher priority (0 = must keep, higher = truncate first)
- Truncation removes content from the end of a section, preserving the beginning

---

## Sample Interactions

```
1. Caller creates a PromptBuilder with a 4096-token budget
2. Caller sets system instruction: "You are a helpful coding assistant."
3. Caller adds context snippets retrieved from a vector database
4. Caller adds tool output: "lint result: 0 errors, 2 warnings"
5. Caller sets user message: "Fix the warnings in my code."
6. Builder estimates total tokens across all sections
7. If over budget:
   - Truncate context snippets (lowest priority) until within budget
   - If still over, truncate tool outputs
   - System instruction and user message are never truncated
8. Builder assembles the final prompt string and returns it
```

---

## Clarifying Questions to Ask

1. "What is the target model's maximum context length?"
2. "Should the token estimator be pluggable or is the word-based heuristic sufficient?"
3. "How should the system handle conflicting variable names across sections?"
4. "Is there a required ordering of sections in the final prompt?"
5. "Should truncation happen at word boundaries or character boundaries?"
6. "Do we need to support multi-turn conversation history as a section type?"
7. "Should the builder be reusable (build multiple prompts) or single-use?"
8. "Are there reserved placeholder names the system should reject?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| PromptTemplate | Parse and safely interpolate named placeholders in a template string |
| TemplateVariable | Metadata about a single placeholder (name, required, default) |
| PromptBuilder | Builder-pattern orchestrator assembling sections into a final prompt |
| PromptSection | A single content block with type, text, priority, and token estimate |
| TokenBudget | Estimate token counts and enforce budget constraints across sections |
| BudgetAllocation | Per-section token budget share and usage tracking |
| TruncationStrategy | Algorithm for reducing a section's content to fit within a token limit |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Template interpolation, token budget, builder with priority truncation, word-boundary truncation |
| v2-extended | Conversation history section, pluggable tokenizer, template inheritance, JSON/XML output formats |
| v3-optimized | Cached token counts, streaming assembly, async builder, multi-model budget profiles |
