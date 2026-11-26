# Design Approach for Safety Filter & Policy Engine

A step-by-step thought process for designing the safety filter and policy engine.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Policy | ✅ Yes | Named rule collection with severity |
| Rule | ✅ Yes | Individual pattern-action pair |
| PolicySet | ✅ Yes | Groups policies for a use case |
| Content Filter | ✅ Yes | Abstract check plugin (Strategy) |
| Keyword Filter | ✅ Yes | Concrete filter for blocked words |
| PII Filter | ✅ Yes | Concrete filter for PII patterns |
| Prompt Injection Filter | ✅ Yes | Concrete filter for injection attacks |
| Rule Violation | ✅ Yes | Result of a single rule match |
| Moderation Result | ✅ Yes | Aggregate decision with breakdown |
| Policy Engine | ✅ Yes | Orchestrator for filter chain |
| Audit Logger | ✅ Yes | Records all decisions |
| Action | ✅ Yes | Enum for decision types |
| Severity | ✅ Yes | Enum for severity levels |
| Dashboard | ❌ No | UI concern, out of scope for v1 |

**Final Entities**: Action, Severity, Rule, Policy, PolicySet, RuleViolation, ContentFilter, KeywordFilter, PIIFilter, PromptInjectionFilter, ModerationResult, PolicyEngine, AuditLogger

---

## Step 2: Define Relationships

```
PolicyEngine (1) ──registers──> (n) ContentFilter
PolicyEngine (1) ──produces──> (n) ModerationResult
PolicyEngine (1) ──uses──> (1) AuditLogger
ContentFilter (1) ──checks against──> (n) Rule
ContentFilter (1) ──produces──> (n) RuleViolation
Policy (1) ──contains──> (n) Rule
PolicySet (1) ──groups──> (n) Policy
ModerationResult (1) ──contains──> (n) RuleViolation
AuditLogger (1) ──records──> (n) ModerationResult
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| PolicyEngine → ContentFilter | Aggregation | Filters exist independently, registered into engine |
| PolicyEngine → AuditLogger | Composition | Logger belongs to engine |
| Policy → Rule | Composition | Rules don't exist without a policy |
| PolicySet → Policy | Aggregation | Policies can belong to multiple sets |
| ContentFilter → RuleViolation | Creates | Filter produces violations |
| ModerationResult → RuleViolation | Aggregation | Result collects all violations |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Chain of Responsibility** | ✅ Yes | Filters form an ordered evaluation pipeline |
| **Strategy** | ✅ Yes | Different filter types implement same interface |
| **Observer** | ✅ Yes | Audit logger observes all moderation decisions |
| **Plugin Architecture** | ✅ Yes | New filters added without changing engine |
| **Factory** | 🔄 v2 | Create filter instances from config |
| **Singleton** | ❌ No | Multiple engines may coexist for different use cases |

### Pattern Application:

1. **Chain of Responsibility** — Filter Pipeline
   - Each `ContentFilter` is a link in the evaluation chain
   - Content passes through every filter in registration order
   - All violations are collected (no short-circuit in v1)

2. **Strategy Pattern** — Content Filters
   - `ContentFilter` ABC defines the `check(text)` interface
   - `KeywordFilter`, `PIIFilter`, `PromptInjectionFilter` are concrete strategies
   - Engine is agnostic to filter internals

3. **Observer Pattern** — Audit Logging
   - `AuditLogger` observes every `evaluate()` call
   - Records input text, timestamp, matched violations, and final decision
   - Decoupled from engine logic

4. **Plugin Architecture** — Extensibility
   - Implement `ContentFilter` to add new check types
   - Register with `engine.add_filter(my_filter)`
   - No engine modification required

---

## Step 4: Design Classes

### Core Classes:

#### PolicyEngine
- **Attributes**:
  - `filters: list[ContentFilter]`
  - `audit_logger: AuditLogger`
- **Methods**:
  - `add_filter(filter: ContentFilter) -> None`
  - `evaluate(text: str) -> ModerationResult`
  - `get_audit_log() -> list[AuditEntry]`

#### ContentFilter (ABC)
- **Attributes**:
  - `name: str`
  - `rules: list[Rule]`
- **Methods**:
  - `check(text: str) -> list[RuleViolation]` (abstract)
  - `get_name() -> str`

#### KeywordFilter
- **Inherits**: ContentFilter
- **Attributes**:
  - `blocked_patterns: list[re.Pattern]`
- **Methods**:
  - `check(text: str) -> list[RuleViolation]`
  - `add_blocked_word(word: str) -> None`

#### PIIFilter
- **Inherits**: ContentFilter
- **Attributes**:
  - `pii_patterns: dict[str, re.Pattern]` (email, phone, SSN)
- **Methods**:
  - `check(text: str) -> list[RuleViolation]`

#### PromptInjectionFilter
- **Inherits**: ContentFilter
- **Attributes**:
  - `injection_patterns: list[re.Pattern]`
- **Methods**:
  - `check(text: str) -> list[RuleViolation]`

#### AuditLogger
- **Attributes**:
  - `entries: list[AuditEntry]`
- **Methods**:
  - `log(entry: AuditEntry) -> None`
  - `get_entries() -> list[AuditEntry]`
  - `clear() -> None`

---

## Step 5: Handle Edge Cases

### Input Validation:
- Empty or whitespace-only text
- Extremely long text inputs
- None/null text input

### Business Logic:
- No filters registered — should return ALLOW
- Multiple filters match same content — collect all violations
- Conflicting actions from different filters — strictest wins
- Case-insensitive matching for keywords and injection patterns
- PII patterns that partially match (e.g., phone-like numbers in ZIP codes)

### Pattern Matching:
- Regex patterns that could cause catastrophic backtracking
- Unicode characters in content
- Patterns that overlap (same text matches keyword + injection)

---

## Step 6: Optimization Opportunities

### Data Structures:
| Operation | Naive | Optimized |
|-----------|-------|-----------|
| Pattern matching | Iterate all patterns | Pre-compiled regex |
| Violation lookup | O(n) list scan | O(1) dict by filter name |
| Audit log search | O(n) linear | O(1) indexed by timestamp |

### Performance:
- Pre-compile all regex patterns at filter creation time
- Short-circuit on BLOCK if early termination is desired (v2)
- Cache compiled patterns across evaluations

### Memory:
- Audit log bounded by configurable max entries (v2)
- Violations reference rules by ID, not full copies

---

## Step 7: Version Progression

### v1-basic
- Core data classes (Action, Severity, Rule, Policy, RuleViolation)
- Three concrete filters (Keyword, PII, PromptInjection)
- PolicyEngine with ordered filter chain
- AuditLogger with in-memory storage
- Runnable demo

### v2-extended
- Confidence-aware triage thresholds (`PrecisionGuardrail`)
- Score/confidence calibration (`DecisionCalibrator.route(...)`)
- Orchestration envelope (`EscalationDecision`) for demote/review semantics
- Backward-compatible action mapping (`map_to_v1_action`)

### v3-optimized
- Async filter evaluation with asyncio
- Pattern compilation cache with LRU
- Persistent audit log (SQLite)
- Metrics collection (filter hit rates, latency)
- Rate limiting per caller

---

## Code Organization

```
safety-filter-policy-engine/
├── PROBLEM.md
├── APPROACH.md
├── DESIGN.md
├── python/
│   ├── v1-basic/
│   │   ├── __init__.py
│   │   ├── policy.py        # Data classes: Action, Severity, Rule, Policy, etc.
│   │   ├── filter.py        # ABC + KeywordFilter, PIIFilter, PromptInjectionFilter
│   │   ├── engine.py        # PolicyEngine, AuditLogger, AuditEntry
│   │   └── demo.py          # Runnable usage examples
│   ├── v2-extended/
│   │   ├── triage.py        # Guardrail and triage decision envelopes
│   │   ├── calibration.py   # Score/confidence to decision routing
│   │   ├── engine_v2.py     # Triage engine + v2-to-v1 action mapper
│   │   └── demo.py          # v2 decision walkthrough
│   └── tests/
│       ├── __init__.py
│       ├── test_safety_filter.py
│       └── test_safety_filter_v2.py
```

---

## Interview Discussion Points

1. **Why Chain of Responsibility over simple iteration?**
   - Explicit ordering guarantees deterministic results
   - Each filter is self-contained and independently testable
   - Easy to reorder, add, or remove filters without touching others

2. **Why Strategy for filters instead of a big switch statement?**
   - Open/Closed Principle: add new filters without modifying engine
   - Each filter encapsulates its own matching logic and rules
   - Enables runtime composition of filter pipelines

3. **Why not short-circuit on first BLOCK?**
   - Collecting all violations provides richer audit data
   - Helps identify content that triggers multiple policies
   - Short-circuit can be added as an optimization flag in v2

4. **How would you add a toxicity classifier?**
   - Implement `ContentFilter` with a `check()` method
   - Internally call an ML model or API (behind an adapter)
   - Register with `engine.add_filter(ToxicityFilter())`
   - No engine changes needed

---

## Implemented v2-Extended Additions (Calibrated Triage)

The shipped `python/v2-extended/` track adds a moderation triage layer without breaking v1:

- `PrecisionGuardrail` models threshold policy for demote/review/block.
- `DecisionCalibrator.route(...)` maps `(score, confidence)` to triage decisions.
- `TriageEngine` produces orchestration-friendly `EscalationDecision`.
- `TriageEngine.map_to_v1_action(...)` preserves compatibility with existing `ALLOW/FLAG/BLOCK` integrations.

Tests are included in `python/tests/test_safety_filter_v2.py`.

---

## v2 Extension Decisions

1. Keep v1 enum (`ALLOW/FLAG/BLOCK`) unchanged for backward compatibility.
2. Add a separate triage envelope for richer moderation actions (`demote`, `review`).
3. Use confidence-aware calibration instead of score-only thresholds.
4. Route review-band decisions to explicit queue namespaces (`review:<context>`).
