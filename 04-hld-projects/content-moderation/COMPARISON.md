# Content Moderation — Comparison Notes

| System | Similarity | Key difference |
|---|---|---|
| [Bot Detection](../bot-detection/) | abuse prevention and adversarial environment | content-level classification vs account-level behavior detection |
| [Video Recommendations](../video-recommendations/) | ranking and policy constraints | safety enforcement objective vs engagement optimization objective |
| [LLM Safety & Eval Platform](../../06-genai-systems/02-llm-hld-projects/llm-safety-eval-platform/) | safety metrics and evaluation loops | app-level moderation runtime vs cross-app governance/control plane |

## Reuse guidance

- Reuse event stream + feedback labeling loop patterns.
- Keep policy engine separated from model-serving internals.
- Share observability primitives with safety/evaluation platforms.
