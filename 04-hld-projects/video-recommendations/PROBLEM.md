# Video Recommendations

## Problem Statement

Design an “up next” video recommendation system that ranks candidate videos for each viewing session to maximize long-term user satisfaction and engagement under strict latency and scale constraints.

---

## Requirements and Constraints

### Functional Requirements

1. Generate personalized recommendation candidates for an active viewing session.
2. Rank candidates using engagement/value objectives.
3. Serve top-k recommendations within tight latency budget.
4. Support exploration safeguards for cold users/videos.
5. Continuously evaluate and update ranking quality.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Recommendation response latency | < 250 ms P95 |
| Availability | 99.9% |
| Scale | 1B DAU class, 1B+ catalog class |
| Result count | top 5 (configurable) |
| Consistency | eventual acceptable for model features |

### Capacity Assumptions

- Candidate universe is too large for full online scoring.
- Multi-stage retrieval/ranking is required.
- Session context shifts quickly and must influence ranking.

### Out of Scope

- Video upload/transcoding/media delivery internals.
- Ads auction system internals.
- Creator payout policy implementation.

### Scope Guardrail

This project is ranking/recommendation architecture only, not streaming delivery architecture.

---

## API / System Interface

```http
POST /api/v1/recommendations/up-next
GET  /api/v1/recommendations/model-metadata
POST /api/v1/recommendations/feedback
GET  /api/v1/recommendations/health
```

---

## Key Design Challenges

1. Multi-stage retrieval/ranking at internet scale.
2. Objective alignment: short-term clicks vs long-term satisfaction.
3. Exploration/exploitation and cold start.
4. Feedback loops and metric lag.

---

## Related Links

- [DESIGN](./DESIGN.md)
- [APPROACH](./APPROACH.md)
- [RUBRIC](./RUBRIC.md)
- [PITFALLS](./PITFALLS.md)
- [FOLLOW-UPS](./FOLLOW-UPS.md)
- [COMPARISON](./COMPARISON.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [News Feed](../news-feed/)
- [Video Streaming](../video-streaming/)
- [Read Scaling](../../03-hld-concepts/read-scaling/)
- [Monitoring & Observability](../../03-hld-concepts/monitoring-observability/)
