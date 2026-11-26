# 🧠 AI Coding Interview Quiz

> **24 questions to test your AI planning, execution, and recovery instincts**
>
> ⏱️ Time: 40 minutes | ⭐⭐⭐⭐ Difficulty

---

## Section 1: Planning & Scope (6 questions)

*Choose the planning move that keeps the interview scoped, measurable, and risk-aware.*

---

### Question 1 ⭐
You are asked to propose an AI coding interview workflow for generating starter problems. What should you do before defining component work?

**A)** Pick the largest model and start writing prompts
**B)** Clarify success metrics (quality thresholds, runtime expectations) with the stakeholder
**C)** Build the UI mockups so reviewers understand the experience
**D)** Create a dataset schema based on personal assumptions

---

### Question 2 ⭐
The dataset you need has only a handful of labeled coding questions. What planning action gives you the best chance of delivering reliably?

**A)** Train a general-purpose completion model and hope it generalizes
**B)** Build a labeling plan that prioritizes high-impact examples and adds active-learning annotations
**C)** Skip data requirements and rely on heuristics from the existing repository
**D)** Ask for more time without changing scope

---

### Question 3 ⭐⭐
To keep assumptions visible during the interview, you should log them where reviewers can discuss discrepancies. Which artifact fits best?

**A)** An assumptions register with owner, confidence level, and mitigation plan
**B)** A single bullet list in your personal notes that you never share
**C)** An informal verbal briefing that you hope stakeholders remember
**D)** Capture them only if the interviewer challenges you

---

### Question 4 ⭐⭐
When multiple objectives compete (speed of feedback, correctness, fairness), how do you prioritize?

**A)** Always optimize for throughput first
**B)** Rank objectives by stakeholder impact and delivery risk, then tackle the highest-value gap
**C)** Delay decision until after building the prototype
**D)** Focus only on the requirements you understand best

---

### Question 5 ⭐⭐⭐
An interviewer asks for a working demo in the same session. What planning strategy keeps you honest?

**A)** Break the scope into a vertical slice that delivers a complete experience end-to-end
**B)** Build as many features as quickly as possible, even if each is shallow
**C)** Prioritize bells and whistles to impress the interviewer
**D)** Skip instrumentation to save time

---

### Question 6 ⭐⭐⭐
Which tracking plan should you include before the first line of code to detect failure early?

**A)** Metrics for request latency, prompt failure rate, and output drift linked to a dashboard
**B)** Only monitor server CPU usage after deployment
**C)** Wait until a bug report arrives before instrumenting
**D)** Track only happy-path success stories

---

## Section 2: Driving AI Work (8 questions)

*Decode the best practices for prompt design, tooling, and production readiness.*

---

### Question 7 ⭐⭐
To keep generated code grounded in requirements, it is best to:

**A)** Ask the model to hallucinate novel features for excitement
**B)** Use retrieval-augmented generation (RAG) so prompts reference canonical docs
**C)** Skip context and rely on the model's internal knowledge
**D)** Hard-code a fixed answer template

---

### Question 8 ⭐⭐
Which architecture best supports verifying inference outputs before returning them to the candidate?

**A)** Direct model output without checks
**B)** A feedback loop that runs generated code against a lightweight test harness
**C)** Save outputs to a log and review manually once per week
**D)** Batch inference only once per session

---

### Question 9 ⭐⭐⭐
During prompt writing, the interviewer wants deterministic reasoning traces. What move improves traceability?

**A)** Use a single short prompt and rely on randomness
**B)** Add explicit step-by-step instructions and an output schema to the prompt
**C)** Request the model to invent arbitrary intermediate steps
**D)** Remove constraints so the model can surprise you

---

### Question 10 ⭐⭐⭐
You're choosing inference infrastructure for live coding support. Which factor deserves the most attention?

**A)** Hosting the largest available model regardless of latency
**B)** Balancing a smaller tuned model with caching and fast retrieval to meet latency targets
**C)** Only using a CPU-based container to save costs
**D)** Avoiding any telemetry to keep infrastructure simple

---

### Question 11 ⭐⭐⭐
What ensures you can debug odd outputs after deployment?

**A)** Capture prompt, response, model metadata, and relevant context in an auditable log
**B)** Rely on users to paste transcripts into bug reports
**C)** Discard prompts to save storage
**D)** Only log metrics that look good

---

### Question 12 ⭐⭐⭐
Which method best helps you measure feature drift in the coding assistant?

**A)** Re-run baseline tests when you remember
**B)** Schedule periodic evaluations that compare live outputs to a golden test-suite
**C)** Assume the model never changes once tuned
**D)** Only check drift if someone complains about a regression

---

### Question 13 ⭐⭐⭐⭐
In an interview, you want to experiment with prompts without destabilizing the main experience. What strategy works?

**A)** Replace the production prompt with every new variant immediately
**B)** Use guard-rail experiments (e.g., shadow prompts or canary users) and compare metrics before rollout
**C)** Stop collecting metrics when iterating
**D)** Hard-code every possible prompt into the main system

---

### Question 14 ⭐⭐⭐⭐
How should you handle a prompt that occasionally introduces toxic language?

**A)** Ignore it because it only happens occasionally
**B)** Add validation checks that reroute flagged content to a human reviewer before sending
**C)** Suppress logging to avoid visibility
**D)** Delete the model without investigating

---

## Section 3: Verification & Testing (6 questions)

*Ensure readiness through reliable testing, fairness checks, and release controls.*

---

### Question 15 ⭐⭐
Which primary metric helps you understand whether generated solutions solve the coding challenge?

**A)** Number of tokens generated
**B)** Test-pass rate on a curated test suite
**C)** Model temperature setting
**D)** Color of the UI

---

### Question 16 ⭐⭐
To validate how the AI agent interacts with a runner, you should:

**A)** Trust the agent without any integration tests
**B)** Build end-to-end tests that include the execution harness and scoring logic
**C)** Skip tests to move faster
**D)** Only rely on manual exploratory sessions

---

### Question 17 ⭐⭐⭐
Before shipping, an AI assistant power is being rolled out gradually. Which approach protects reliability?

**A)** Deploy to 100% of traffic immediately
**B)** Use a canary population and monitor key metrics for degradation
**C)** Turn off monitoring to avoid noise
**D)** Roll back only after catastrophic failure

---

### Question 18 ⭐⭐⭐
How can you verify the system resists adversarial prompts designed to trick it into incorrect code?

**A)** Assume the model is safe by default
**B)** Maintain an adversarial prompt suite and run it during regression testing
**C)** Only test with happy-path prompts
**D)** Remove logging to avoid revealing vulnerabilities

---

### Question 19 ⭐⭐⭐
What practice ensures you can reproduce a mismatch between prompt and dataset versions?

**A)** Never version datasets and rely on manual recall
**B)** Snapshot prompts, model config, and dataset IDs alongside every release
**C)** Store only the latest dataset without history
**D)** Avoid metadata to reduce storage

---

### Question 20 ⭐⭐⭐⭐
You need a quality gate for release readiness. What is the best signal?

**A)** Subjective gut feeling
**B)** A minimum threshold (e.g., 90%) on automated correctness and hallucination detection checks
**C)** Deploy as soon as code compiles
**D)** Release only when all stakeholders are asleep

---

## Section 4: Communication & Recovery (4 questions)

*Maintain transparency, plan fallbacks, and coordinate across teams when things go wrong.*

---

### Question 21 ⭐⭐
During a demo, the AI helper starts producing nonsense. What is your immediate communication?

**A)** Hide the issue and move on
**B)** Acknowledge the failure, note the current behavior, and explain the fallback (e.g., revert to a safe baseline)
**C)** Blame the model without evidence
**D)** Pretend it never happened

---

### Question 22 ⭐⭐⭐
An interviewer asks about a safety trade-off you are unsure about. What do you say?

**A)** Guess a confident yes/no answer
**B)** Share what you know, outline where uncertainty remains, and propose next steps (experiments or research)
**C)** Claim the system already solves it perfectly
**D)** Change the topic to performance

---

### Question 23 ⭐⭐⭐
Halfway through a build, stakeholders request a new constraint. How do you respond?

**A)** Promise to add it without updating the plan
**B)** Re-estimate the impact, highlight trade-offs, and update the scope or timeline accordingly
**C)** Ignore the request
**D)** Remove another feature without discussion

---

### Question 24 ⭐⭐⭐⭐
How do you keep cross-functional collaborators informed during the interview build?

**A)** Keep all updates in your head
**B)** Send concise asynchronous summaries with blockers, decisions, and next actions
**C)** Only communicate via long multi-page documents
**D)** Wait for weekly meetings only

---
