# Design Approach for Prompt Builder

A step-by-step thought process for designing the prompt assembly system.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Prompt | ❌ No | The output string — not an entity we model |
| Template | ✅ Yes | Reusable text pattern with placeholders |
| Placeholder / Variable | ✅ Yes | Named slot inside a template |
| Section | ✅ Yes | A logical content block (system, user, context, tools) |
| Builder | ✅ Yes | Orchestrator assembling sections into a prompt |
| Token Budget | ✅ Yes | Constraint tracker for context length |
| Budget Allocation | ✅ Yes | Per-section share of the total budget |
| Truncation Strategy | ✅ Yes | Algorithm for trimming content |
| LLM / Model | ❌ No | External consumer — out of scope |

**Final Entities (v1)**: PromptTemplate, TemplateVariable, PromptSection, PromptBuilder, TokenBudget, BudgetAllocation

---

## Step 2: Define Relationships

```
PromptTemplate (1) ──contains──> (n) TemplateVariable
PromptBuilder (1) ──assembles──> (n) PromptSection
PromptBuilder (1) ──uses──> (1) TokenBudget
TokenBudget (1) ──tracks──> (n) BudgetAllocation
PromptSection (1) ──optionally uses──> (1) PromptTemplate
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| PromptTemplate → TemplateVariable | Composition | Variables don't exist outside their template |
| PromptBuilder → PromptSection | Composition | Sections belong to the builder instance |
| PromptBuilder → TokenBudget | Aggregation | Budget is injected and could be shared |
| TokenBudget → BudgetAllocation | Composition | Allocations are owned by the budget |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Builder** | ✅ Yes | Fluent section-by-section prompt assembly |
| **Strategy** | ✅ Yes | Pluggable truncation algorithms |
| **Template Method** | ✅ Yes | Common render flow with variable interpolation hook |
| **Factory** | 🔄 v2 | Create builders from config profiles |
| **Observer** | ❌ No | No event-driven needs in v1 |
| **Singleton** | ❌ No | No global state — prefer dependency injection |

### Pattern Application:

1. **Builder Pattern** — PromptBuilder
   - `set_system_instruction()`, `add_context_snippet()`, `set_user_message()`, `add_tool_output()`
   - `build()` returns the assembled prompt string
   - Fluent interface: each setter returns `self` for chaining

2. **Strategy Pattern** — Truncation
   - `EndTruncation` removes content from the end of a section
   - Future strategies: `MiddleTruncation`, `SentenceBoundaryTruncation`
   - `TokenBudget` delegates to the active strategy when trimming

3. **Template Method** — PromptTemplate
   - Common flow: parse placeholders → validate variables → substitute
   - Subclasses could override parsing for different placeholder syntaxes

---

## Step 4: Design Classes

### Core Classes:

#### TemplateVariable (dataclass)
- **Attributes**:
  - `name: str` — placeholder identifier
  - `required: bool` — whether omission is an error
  - `default: str` — fallback value when not provided
- **Methods**: None (pure data carrier)

#### PromptTemplate
- **Attributes**:
  - `template_str: str` — raw template text with `{placeholders}`
  - `variables: List[TemplateVariable]` — discovered placeholders
- **Methods**:
  - `render(values: Dict[str, str]) → str` — safe interpolation
  - `_parse_placeholders() → List[TemplateVariable]` — extract placeholder names
  - `_validate(values) → None` — check required variables are present
- **Safety**: Uses regex substitution, never `str.format()` with user data

#### PromptSection (dataclass)
- **Attributes**:
  - `name: str` — section identifier (e.g., "system", "context")
  - `content: str` — section text
  - `priority: int` — truncation order (0 = keep, higher = truncate first)
  - `token_count: int` — estimated tokens
- **Methods**: None (pure data carrier)

#### BudgetAllocation (dataclass)
- **Attributes**:
  - `section_name: str` — which section this allocation covers
  - `max_tokens: int` — maximum allowed tokens
  - `used_tokens: int` — currently consumed tokens
- **Methods**:
  - `remaining() → int` — tokens still available

#### TokenBudget
- **Attributes**:
  - `max_tokens: int` — total context-length budget
  - `allocations: Dict[str, BudgetAllocation]` — per-section budgets
  - `token_estimator: Callable[[str], int]` — pluggable estimator function
- **Methods**:
  - `estimate_tokens(text: str) → int` — count tokens in text
  - `allocate(section_name, max_tokens) → None` — register a section budget
  - `fits(section_name, text) → bool` — check if text fits within allocation
  - `truncate_to_fit(text, max_tokens) → str` — trim text to fit budget

#### PromptBuilder
- **Attributes**:
  - `_sections: Dict[str, PromptSection]` — named sections
  - `_context_snippets: List[str]` — retrieved context pieces
  - `_tool_outputs: List[str]` — tool result strings
  - `_budget: TokenBudget` — budget tracker
- **Methods**:
  - `set_system_instruction(text) → PromptBuilder`
  - `set_user_message(text) → PromptBuilder`
  - `add_context_snippet(text) → PromptBuilder`
  - `add_tool_output(text) → PromptBuilder`
  - `build() → str` — assemble, truncate if needed, return final prompt

---

## Step 5: Handle Edge Cases

### Input Validation:
- Empty or whitespace-only template strings
- Placeholder names with invalid characters
- Negative or zero token budgets
- Missing required template variables

### Business Logic:
- Total sections exceed budget — trigger priority-based truncation
- All sections are high-priority — truncation cannot satisfy budget (raise error)
- Empty context snippets list — omit context section entirely
- Duplicate section names — later set overwrites earlier
- Template with no placeholders — return as-is

### Boundary Conditions:
- Budget exactly equals total section tokens — no truncation needed
- Single very large section consuming entire budget
- Unicode text with multi-byte characters
- Template variable value containing placeholder-like syntax (`{foo}`) — must NOT be re-interpolated

---

## Step 6: Optimization Opportunities

### Data Structures:

| Operation | v1 Basic | v3 Optimized |
|-----------|----------|--------------|
| Token estimation | O(n) word split | O(1) cached |
| Template render | O(n) regex sub | O(n) pre-compiled |
| Truncation | O(n) re-estimate | O(1) with index |
| Build prompt | O(s × n) | O(s) with caching |

*n = text length in characters, s = number of sections*

### Caching:
- Cache token counts per section; invalidate on content change
- Pre-parse template placeholders on construction

### Safety:
- Compile placeholder regex once and reuse
- Escape user values before interpolation to prevent injection

---

## Step 7: Version Progression

### v1-basic
- Safe regex-based template interpolation
- Word-based token estimation (`words × 1.3`)
- Builder with four section types
- End-truncation strategy
- Priority-based budget enforcement

### v2-extended
- Conversation history as a section type
- Pluggable tokenizer interface (tiktoken adapter)
- Template inheritance (base + overlay)
- JSON and XML output format support
- Lenient mode for missing variables

### v3-optimized
- Cached token counts with dirty-flag invalidation
- Streaming assembly for very large prompts
- Async builder for concurrent section fetching
- Multi-model budget profiles (GPT-4, Claude, Llama)

---

## Code Organization

```
prompt-builder/
├── PROBLEM.md                  # Requirements and constraints
├── APPROACH.md                 # This design walkthrough
├── DESIGN.md                   # Class diagrams and decisions
├── python/
│   ├── v1-basic/
│   │   ├── __init__.py         # Package marker
│   │   ├── template.py         # PromptTemplate, TemplateVariable
│   │   ├── budget.py           # TokenBudget, BudgetAllocation
│   │   ├── prompt_builder.py   # PromptBuilder, PromptSection
│   │   └── demo.py             # Runnable end-to-end example
│   └── tests/
│       ├── __init__.py         # Package marker
│       └── test_prompt_builder.py  # Unit tests for all components
```

---

## Interview Discussion Points

1. **Why Builder for PromptBuilder?**
   - Prompts are assembled incrementally from heterogeneous parts
   - Fluent interface makes the API self-documenting
   - Separates construction logic from the final product representation

2. **Why not use Python's `str.format()` or f-strings?**
   - `str.format_map()` can invoke `__format__` on arbitrary objects
   - f-strings execute expressions — a direct injection risk
   - Regex-based substitution is purely textual and auditable

3. **Why word-based token estimation?**
   - Real tokenizers (tiktoken) are external dependencies
   - The `words × 1.3` heuristic is widely used for English text
   - The estimator is pluggable — callers can inject tiktoken in production

4. **How would you handle multi-turn conversations?**
   - Add a `ConversationSection` that holds a list of turn objects
   - Each turn has a role (user/assistant) and content
   - Budget allocation respects a sliding window of recent turns
