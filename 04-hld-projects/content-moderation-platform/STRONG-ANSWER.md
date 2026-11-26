# Content Moderation Platform — Strong Answer Outline

Say: "I will separate real-time enforcement from slower policy review and model improvement, because a platform needs fast protection, explainable actions, and measurable policy quality."

## Suggested Interview Narrative

1. **Requirements:** action ladder + precision guardrail for irreversible actions.
2. **Estimation:** throughput plus limited reviewer capacity.
3. **API/Data model:** explicit score-confidence-decision contract with audit timeline.
4. **Architecture:** inference -> calibrator -> enforcement + review lane.
5. **Deep dives:** queue prioritization, drift detection, staged rollback.
6. **Wrap-up:** safety vs latency/cost trade-off and 10x bottleneck.
