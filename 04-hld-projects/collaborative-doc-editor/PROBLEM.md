# Collaborative Document Editor

## Problem Statement

Design a browser-based collaborative editor where multiple users can edit the same document concurrently with low-latency updates and eventual convergence.

---

## Requirements and Constraints

### Functional Requirements

1. Users can create and open documents.
2. Multiple users can edit the same document concurrently.
3. Users can see other collaborators' updates and cursor presence in near real time.
4. Documents remain available after service restart.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Edit propagation latency | < 100 ms P99 |
| Durability for saved state | Strong |
| Consistency model | Eventual convergence |
| Concurrent editors/document | <= 100 active editors |
| Availability | 99.95% |

### Capacity Assumptions

- Millions of concurrent websocket connections.
- Billions of documents total.
- Highly skewed active-document distribution.

### Out of Scope

- Full ACL/permission matrix.
- Rich document formatting fidelity.
- Full revision UI and branchable version history.

---

## High-Level Design Outline

### Core Services

- API Gateway
- Document Metadata Service
- Collaboration Session Service
- Operation Processor (OT/transform pipeline)
- Snapshot and Persistence Service

### API Surface (Illustrative)

```http
POST /api/v1/documents
GET /api/v1/documents/{documentId}
WS /api/v1/documents/{documentId}/session
```

---

## Scoring Rubric (Quick Signals)

1. Clear convergence strategy under concurrent edits.
2. Correct handling of connection/session scaling.
3. Durable snapshot and replay story.
4. Explicit boundaries between metadata CRUD and realtime collaboration path.

See [RUBRIC](./RUBRIC.md).

---

## Common Pitfalls

- Assuming single-writer semantics.
- Treating websocket delivery order as global consistency.
- Missing reconnect replay protocol.

See [PITFALLS](./PITFALLS.md).

---

## Follow-Up Questions

- How do we scale sessions across many collaboration nodes?
- How do we recover from node loss during active edits?
- What changes if we add full document history playback?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Variants and Extensions

- Reader-only overflow mode for very large sessions.
- Comment/annotation stream.
- Offline edit queue and sync reconciliation.

---

## Related Links

- [DESIGN](./DESIGN.md)
- [APPROACH](./APPROACH.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/real-time-updates](../../03-hld-concepts/real-time-updates/)
- [03-hld-concepts/consistent-hashing](../../03-hld-concepts/consistent-hashing/)
- [03-hld-concepts/workflow-orchestration](../../03-hld-concepts/workflow-orchestration/)
