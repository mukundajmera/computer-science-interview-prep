# 🧠 AI Coding Interview Quiz - Answer Key

> **Concise rationales for the 24 AI readiness questions**

---

## Section 1: Planning & Scope

### Question 1
**Answer: B) Clarify success metrics (quality thresholds, runtime expectations) with the stakeholder**
Starting with clear acceptance criteria prevents misalignment and exposes hard constraints before design.

### Question 2
**Answer: B) Build a labeling plan that prioritizes high-impact examples and adds active-learning annotations**
A focused labeling effort balances quality and speed when data is scarce.

### Question 3
**Answer: A) An assumptions register with owner, confidence level, and mitigation plan**
Documented assumptions make trade-offs transparent and easier to revisit.

### Question 4
**Answer: B) Rank objectives by stakeholder impact and delivery risk, then tackle the highest-value gap**
Prioritizing on impact plus risk keeps work focused where flexibility is limited.

### Question 5
**Answer: A) Break the scope into a vertical slice that delivers a complete experience end-to-end**
A vertical slice proves system viability quickly while leaving room for iteration.

### Question 6
**Answer: A) Metrics for request latency, prompt failure rate, and output drift linked to a dashboard**
Predefined observability prevents silent failure and keeps you proactive.

---

## Section 2: Driving AI Work

### Question 7
**Answer: B) Use retrieval-augmented generation (RAG) so prompts reference canonical docs**
Embedding authoritative context constrains responses to known requirements.

### Question 8
**Answer: B) A feedback loop that runs generated code against a lightweight test harness**
Automated verification before responding improves confidence in outputs.

### Question 9
**Answer: B) Add explicit step-by-step instructions and an output schema to the prompt**
Structured prompts yield reproducible reasoning traces.

### Question 10
**Answer: B) Balancing a smaller tuned model with caching and fast retrieval to meet latency targets**
Pragmatic sizing plus retrieval delivers predictable response times.

### Question 11
**Answer: A) Capture prompt, response, model metadata, and relevant context in an auditable log**
Comprehensive logs enable post-mortem debugging without guesses.

### Question 12
**Answer: B) Schedule periodic evaluations that compare live outputs to a golden test-suite**
Scheduled regression checks surface drift early.

### Question 13
**Answer: B) Use guard-rail experiments (e.g., shadow prompts or canary users) and compare metrics before rollout**
Isolated experiments let you validate changes without breaking the main path.

### Question 14
**Answer: B) Add validation checks that reroute flagged content to a human reviewer before sending**
Safety tooling with human review limits toxic outputs while you investigate root cause.

---

## Section 3: Verification & Testing

### Question 15
**Answer: B) Test-pass rate on a curated test suite**
Correctness drives interview outcomes more than superficial metrics.

### Question 16
**Answer: B) Build end-to-end tests that include the execution harness and scoring logic**
End-to-end coverage detects interface issues that unit tests miss.

### Question 17
**Answer: B) Use a canary population and monitor key metrics for degradation**
Canaries validate behavior under controlled risk.

### Question 18
**Answer: B) Maintain an adversarial prompt suite and run it during regression testing**
Active adversarial testing catches regressions before release.

### Question 19
**Answer: B) Snapshot prompts, model config, and dataset IDs alongside every release**
Versioned artifacts allow exact reproduction of past behaviors.

### Question 20
**Answer: B) A minimum threshold (e.g., 90%) on automated correctness and hallucination detection checks**
Objective quality gates keep reliability predictable.

---

## Section 4: Communication & Recovery

### Question 21
**Answer: B) Acknowledge the failure, note the current behavior, and explain the fallback (e.g., revert to a safe baseline)**
Transparency plus a defined fallback reduces stakeholder anxiety.

### Question 22
**Answer: B) Share what you know, outline where uncertainty remains, and propose next steps (experiments or research)**
Honest gaps plus action items show strong judgment.

### Question 23
**Answer: B) Re-estimate the impact, highlight trade-offs, and update the scope or timeline accordingly**
Replanning respects the new constraint while keeping everyone aligned.

### Question 24
**Answer: B) Send concise asynchronous summaries with blockers, decisions, and next actions**
Regular, focused updates keep cross-functional teams coordinated.
