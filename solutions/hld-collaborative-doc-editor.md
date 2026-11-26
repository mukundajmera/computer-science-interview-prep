# 🏆 Coach Answer: Collaborative Document Editor — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (5 min)

### Functional

1. Create/open docs.
2. Concurrent editing.
3. Presence and cursor updates.
4. Durable document state.

### Non-Functional

| Metric | Target |
|---|---|
| Edit propagation | < 100ms |
| Concurrency model | Eventual convergence |
| Active editors/doc | <= 100 |
| Availability | 99.95% |

---

## Phase 2 — Capacity (5 min)

- Millions of websocket connections.
- Billions of stored documents.
- High skew by active document.

---

## Phase 3 — APIs (5 min)

```http
POST /api/v1/documents
GET /api/v1/documents/{documentId}
WS /api/v1/documents/{documentId}/session
```

---

## Phase 4 — Data Model (5 min)

- `Document(document_id, version, snapshot_ref)`
- `Operation(op_id, document_id, base_version, payload)`
- `SessionMember(document_id, user_id, cursor)`

---

## Phase 5 — Architecture (10 min)

- Session gateway with document affinity routing.
- Operation transform/apply processor.
- Operation log + snapshot compaction.

---

## Phase 6 — Deep Dives (10 min)

1. Convergence strategy for concurrent edits.
2. Reconnect replay protocol.
3. Session failover with bounded recovery.

---

## Phase 7 — Trade-Off Wrap (5 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Realtime transport | WebSocket | Polling | Low latency collaboration |
| Persistence model | Operation log + snapshots | Snapshot-only | Better recovery |
| Concurrency control | Transform pipeline | Single writer | Better collaborative UX |
