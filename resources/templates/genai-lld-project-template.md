# GenAI LLD Project Template

Use this for GenAI low-level design projects under `06-genai-systems/01-llm-lld-projects/`.

## Required Files

- `PROBLEM.md`
- `APPROACH.md`
- `DESIGN.md`
- `CODE-WALKTHROUGH.md`
- `RUBRIC.md`
- `PITFALLS.md`
- `FOLLOW-UPS.md`
- Python implementation and tests

## Required Design Signals

- Public API and data contracts.
- Model/client abstraction boundaries.
- Prompt/template ownership.
- Retry, timeout, and fallback behavior.
- Evaluation hooks.
- Safety checks.
- Cost and latency controls.
- Test doubles for model-dependent behavior.

## Done Gate

Python tests must pass, model calls must be mockable/offline, and currentness/safety sections must be present.
