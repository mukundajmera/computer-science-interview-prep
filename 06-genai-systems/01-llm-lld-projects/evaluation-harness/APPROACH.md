# Design Approach for LLM Evaluation Harness

A step-by-step thought process for designing the evaluation harness.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Test Case | ✅ Yes | Single evaluation example with input and expected output |
| Test Suite | ✅ Yes | Named collection of test cases for batch evaluation |
| Model Adapter | ✅ Yes | Abstract interface to any LLM or stub |
| Metric | ✅ Yes | Scoring algorithm that produces a 0–1 score |
| Evaluation Result | ✅ Yes | Per-case outcome including scores and pass/fail |
| Evaluation Report | ✅ Yes | Aggregate report across a suite run |
| Evaluation Runner | ✅ Yes | Orchestrator that drives generation and scoring |
| Tag | ❌ No | Simple string — not a first-class entity |
| Embedding | ❌ No | Not relevant to evaluation scoring |
| Pipeline | 🔄 v2 | Orchestration wrapper — deferred to v2 |

**Final Entities (v1)**: TestCase, TestSuite, ModelAdapter, EchoAdapter, StaticAdapter, Metric, ExactMatchMetric, NGramOverlapMetric, KeywordPresenceMetric, LengthComplianceMetric, CustomMetric, EvaluationResult, EvaluationReport, EvaluationRunner

---

## Step 2: Define Relationships

```
TestSuite (1) ──contains──> (n) TestCase
EvaluationRunner (1) ──uses──> (1) ModelAdapter
EvaluationRunner (1) ──applies──> (n) Metric
EvaluationRunner (1) ──evaluates──> (1) TestSuite
EvaluationRunner (1) ──produces──> (1) EvaluationReport
EvaluationReport (1) ──contains──> (n) EvaluationResult
EvaluationResult (1) ──derived from──> (1) TestCase
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| TestSuite → TestCase | Composition | Cases don't exist independently of a suite |
| EvaluationRunner → ModelAdapter | Association | Adapter injected at construction |
| EvaluationRunner → Metric | Association | Metrics injected at construction |
| EvaluationReport → EvaluationResult | Composition | Results belong to the report |
| EvaluationResult → TestCase | Derivation | Result carries case data plus actual output |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Strategy** | ✅ Yes | Swap metrics and model adapters without changing the runner |
| **Template Method** | ✅ Yes | Runner orchestrates generate → score → aggregate with fixed flow |
| **Observer** | 🔄 v2 | Notify listeners on each result (logging, progress bars) |
| **Factory** | 🔄 v2 | Create metrics by name string |
| **Singleton** | ❌ No | No global state — prefer dependency injection |
| **Builder** | 🔄 v2 | Complex runner configuration in v2 |

### Pattern Application:

1. **Strategy Pattern** — Metric
   - `ExactMatchMetric`, `NGramOverlapMetric`, `KeywordPresenceMetric`, `LengthComplianceMetric`, `CustomMetric` share the same `score()` interface
   - `EvaluationRunner` iterates over any list of metrics
   - Easy to add `RougeMetric` or `BERTScoreStub` later

2. **Strategy Pattern** — ModelAdapter
   - `EchoAdapter`, `StaticAdapter`, and future real API adapters share `generate()`
   - Runner is completely decoupled from how outputs are produced

3. **Template Method** — EvaluationRunner
   - `evaluate_case` follows a fixed sequence: generate → time → score → pass/fail
   - `evaluate_suite` calls `evaluate_case` per case, then aggregates
   - Subclasses could override hooks (e.g., pre-process prompts) without changing flow

---

## Step 4: Design Classes

### Core Classes:

#### TestCase (dataclass)
- **Attributes**:
  - `case_id: str` — unique identifier (auto-generated UUID)
  - `input_text: str` — prompt to send to the model
  - `expected_output: str` — ground-truth answer
  - `tags: List[str]` — category labels for filtering
  - `metadata: Dict[str, str]` — arbitrary extra context
- **Methods**: None (pure data carrier)

#### TestSuite
- **Attributes**:
  - `name: str` — suite identifier
  - `test_cases: List[TestCase]` — ordered collection
- **Methods**:
  - `add_case(case) → None` — append a case
  - `filter_by_tag(tag) → List[TestCase]` — subset by tag
  - `size() → int` — count of cases

#### ModelAdapter (ABC)
- **Methods**:
  - `generate(input_text: str) → str` — produce output from prompt

#### EchoAdapter / StaticAdapter
- Concrete stubs for testing. Echo returns input; Static returns a fixed string.

#### Metric (ABC)
- **Properties**: `name: str` — metric identifier
- **Methods**: `score(expected, actual) → float` — score in [0.0, 1.0]

#### ExactMatchMetric
- Case-insensitive by default; configurable via `case_sensitive` flag.
- Returns `1.0` on match, `0.0` otherwise.

#### NGramOverlapMetric
- Configurable `n` (default 1). Tokenises by whitespace, lowercases.
- Computes precision: fraction of expected n-grams found in actual.

#### KeywordPresenceMetric
- Accepts a list of keywords. Scores as fraction found (case-insensitive substring).

#### LengthComplianceMetric
- Configurable `min_length` and `max_length`. Binary: `1.0` if within range, `0.0` otherwise.

#### CustomMetric
- Wraps a caller-supplied `Callable[[str, str], float]`. Clamps output to [0.0, 1.0].

#### EvaluationResult (dataclass)
- Captures `case_id`, `input_text`, `expected_output`, `actual_output`, per-metric `scores`, `passed`, `duration_ms`.

#### EvaluationReport (dataclass)
- Captures `suite_name`, `results`, `aggregate_scores`, `pass_rate`, `total_duration_ms`, `timestamp`.

#### EvaluationRunner
- Injected with `ModelAdapter` and `List[Metric]`.
- `evaluate_case`: generate → time → score each metric → determine pass/fail.
- `evaluate_suite`: loop over cases → build report with aggregates.
- `compare_reports`: diff aggregate scores to detect regressions.

---

## Step 5: Handle Edge Cases

### Input Validation:
- Empty `input_text` or `expected_output` — metrics should still compute (may return 0.0)
- No metrics configured — runner should return results with empty scores dict
- Empty test suite — report should have zero results, 0.0 pass rate, no aggregates

### Business Logic:
- All metrics score identically for identical expected/actual → 1.0
- N-gram overlap with `n` larger than token count → 0.0
- Keywords list is empty → score 1.0 (vacuously true)
- Custom metric function raises exception → catch and score 0.0
- Model adapter raises exception → catch, score 0.0, mark as failed

### Boundary Conditions:
- Very long outputs (performance should remain linear)
- Unicode text with multi-byte characters
- Pass threshold of 0.0 (everything passes) or 1.0 (nearly nothing passes)
- Single-case suite
- Suite with all passing or all failing cases

---

## Step 6: Optimisation Opportunities

### Data Structures:

| Operation | v1 Basic | v3 Optimized |
|-----------|----------|--------------|
| Evaluate single case | O(m · n) | O(m · n) |
| Evaluate suite | O(k · m · n) | O(k · m · n) async |
| Aggregate report | O(k · m) | O(k · m) |
| Compare reports | O(m) | O(m) |

*k = cases, m = metrics, n = average output length*

### Caching:
- Cache model outputs by input hash to avoid re-generating for the same prompt
- Pre-compute n-gram sets for expected outputs if reused across runs

### Aggregation:
- Running mean avoids a second pass over results
- Per-metric accumulators reduce memory for very large suites

---

## Step 7: Version Progression

### v1-basic
- Five metric implementations (exact match, n-gram overlap, keyword presence, length compliance, custom)
- Two model adapter stubs (echo, static)
- Test suite with tag filtering
- Runner producing per-case results and aggregate reports
- Report comparison for regression detection

### v2-extended
- Slice-aware generalization evaluation
- Drift signal computation with severity tiers
- Tolerance-aware regression comparison
- Additive API that preserves v1 compatibility

### v3-optimized
- Async evaluation with `asyncio`
- Streaming metric computation for very long outputs
- Persistent report store (JSON file-backed)
- Dashboard-ready output format
- Statistical significance testing for regression detection

---

## Code Organisation

```
evaluation-harness/
├── PROBLEM.md                  # Requirements and constraints
├── APPROACH.md                 # This design walkthrough
├── DESIGN.md                   # Class diagrams and decisions
├── python/
│   ├── v1-basic/
│   │   ├── __init__.py         # Package marker
│   │   ├── test_case.py        # TestCase, TestSuite
│   │   ├── model_adapter.py    # ModelAdapter ABC, EchoAdapter, StaticAdapter
│   │   ├── metrics.py          # Metric ABC and five implementations
│   │   ├── runner.py           # EvaluationResult, EvaluationReport, EvaluationRunner
│   │   └── demo.py             # Runnable end-to-end example
│   ├── v2-extended/
│   │   ├── generalization.py   # Temporal slices and generalization reports
│   │   ├── drift.py            # Drift signals and severity classification
│   │   ├── runner_v2.py        # Tolerance-aware regression comparisons
│   │   └── demo.py             # v2 slice/drift walkthrough
│   └── tests/
│       ├── __init__.py         # Package marker
│       ├── test_evaluation_harness.py  # Unit tests for all components
│       └── test_evaluation_harness_v2.py  # v2 slice/drift tests
```

---

## Interview Discussion Points

1. **Why Strategy for Metrics?**
   - Different evaluation goals require different scoring criteria
   - Callers compose any set of metrics without touching runner code
   - Follows Open/Closed Principle — add a `RougeMetric` tomorrow

2. **Why an ABC for ModelAdapter?**
   - Production harnesses target different LLM providers
   - A clean interface lets us develop scoring logic against the abstraction
   - Stub adapters keep tests fast and dependency-free

3. **Why not call real LLM APIs?**
   - API access is an infrastructure concern, not a design concern
   - Keeping the adapter as a simple `generate → str` interface focuses the design
   - Callers can plug in any provider behind the abstraction

4. **How would you add persistence?**
   - Serialise `EvaluationReport` to JSON (all fields are primitives or lists of primitives)
   - Load baseline reports from disk for regression comparison
   - No changes to runner or metric code

---

## v2 Extension Decisions

1. Add a dedicated slice-evaluation module instead of overloading v1 metrics.
2. Keep drift logic explicit (`DriftSignal`) so alerting can use severity tiers.
3. Add tolerance-aware regression checks to avoid noisy false alarms.
4. Keep v2 API additive to preserve v1 tests and demo compatibility.

5. **How does this relate to the HLD Evaluation Platform?**
   - This harness is one component in a larger system
   - The [HLD platform](../../02-llm-hld-projects/llm-evaluation-safety-platform/) adds scheduling, storage, dashboards, and safety checks
   - Clean separation means this module can be deployed independently or embedded

---

## Implemented v2-Extended Additions (Generalization + Drift)

The repository now ships a concrete `python/v2-extended/` track focused on production interview follow-ups around quality degradation:

- `TemporalSliceEvaluator.evaluate(...)` evaluates quality on cohort/time slices.
- `DriftDetector.compute(...)` computes delta/relative drift and severity.
- `compare_reports_with_tolerance(...)` gates regressions with explicit tolerance.
- Core types: `GeneralizationSlice`, `GeneralizationReport`, `DriftSignal`.

This keeps v1 contract intact while adding interview-grade diagnostics for generalization and model drift.
