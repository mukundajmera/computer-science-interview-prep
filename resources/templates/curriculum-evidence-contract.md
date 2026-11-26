# Curriculum Evidence Contract

This document defines the shared expectations (the "contract") for all authoritative curriculum templates (HLD, LLD, Concepts, and GenAI). Its purpose is to ensure correctness-first learning by strictly separating verified facts from assumptions, establishing clear layers of depth, and preventing arbitrary constraints (like minimum line counts or universal multi-doc mandates).

When creating or modifying curriculum materials, authors and reviewers must ensure the content adheres to the following contract fields.

---

## 1. 📚 Topic Level & Prerequisites
- **Layering:** Every artifact must clearly and explicitly state its target layer:
  - **Beginner:** Intuitive minimum examples, focusing on the "what" and "how".
  - **Core:** Standard interview readiness, focusing on trade-offs and scaling limits.
  - **Staff (Optional):** Deep dives, complex failure domain interactions, and multi-region nuances. Staff analysis is **optional** and should not be mandated universally.
- **Prerequisites:** Explicitly list necessary foundational concepts or precursor projects.

## 2. 🎯 Scope & Non-Goals
- **In Scope:** The precise boundaries of the system or concept being modeled.
- **Out of Scope (Non-Goals):** Explicitly list features, edge cases, or platform concerns that are deliberately ignored (e.g., "live cloud deployment," "production performance guarantees").

## 3. 📊 Scenario Assumptions vs. Externally Measured Facts
- **Scenario Assumptions:** Capacity (DAU), latency targets, accuracy expectations, data size, and throughput figures provided in prompts or examples must be treated as **assumptions** for the sake of the scenario. They are not universal facts.
- **Calculations & Units:** Any back-of-the-envelope calculations must explicitly list variables, show the formula used, and compute units correctly. Inconsistent math must be corrected, not just copied from the prompt.
- **External Facts:** Hard limits (e.g., maximum IPv4 addresses, theoretical network bandwidth limits) must be verifiable.

## 4. 🔗 Provenance & Ownership
- **Primary-Source Version/Date:** If referencing external tools, papers, or systems (e.g., "DynamoDB," "Spanner paper"), provide a specific version, date, or epoch to anchor the context.
- **Diagram-Source Ownership:** Diagrams must be sourced from internal `.mmd` files in the `diagrams/` folder. Do not embed external unowned images.

## 5. 🔬 Invariants, Traces, & Code Parity
- **Named Invariants:** What state or property must absolutely hold true for the system to be considered correct? (e.g., "No two generated IDs are identical").
- **Normal, Failure, & Evidence Traces:**
  - **Normal Trace:** The expected, happy-path sequence of operations.
  - **Failure Trace:** Explicit tracing of what happens when dependencies fail, clocks roll back, or network partitions occur.
  - **Evidence Trace:** Mapped sources for verified metrics and testing contracts without arbitrary line counts.
- **Code Parity (When Applicable):** LLD and code-based projects must maintain Java 11+ and Python 3.8+ parity. GenAI materials follow a Python-first policy.
- **HLD Rule:** HLD designs remain **docs-only**. Do not include executable simulation scripts in HLD packs unless an explicit policy exception is granted.

## 6. ✅ Verification & Evidence
- **Machine Checks:** Format, syntax, directory structure, and basic compilation/test-execution are validated via scripts (e.g., `scripts/check_curriculum_task.py`). These checks intentionally avoid arbitrary line counts.
- **Semantic Review:** Machine checks cannot guarantee correctness. A separately recorded semantic review (by a human or authorized orchestrator) must independently verify trade-off reasoning, assumption validity, and adherence to named invariants.

---

*Note to Contributors: This contract replaces arbitrary length requirements or universal "8-doc pack" mandates. Focus on correctness, clear boundaries, and verifiable traces.*
