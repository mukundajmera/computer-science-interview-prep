# Collaborative Document Editor — Interview Approach

## 1. Lock Scope

- Confirm simple text model for v1.
- Confirm max active editors per doc and persistence expectations.
- Separate document metadata APIs from realtime operation channel.

## 2. Estimate Scale

- Active sessions and websocket counts.
- Per-document operation rate at peak collaboration.
- Snapshot frequency and storage growth assumptions.

## 3. Define Entities and Protocol

- Entities: `Document`, `Operation`, `SessionMember`, `Snapshot`.
- Protocol: websocket operation frames with monotonic operation IDs.

## 4. Architecture

- Session routing by `document_id`.
- Operation transform/apply pipeline.
- Snapshot persistence + replay on reconnect.

## 5. Deep Dives

1. Concurrent edit convergence.
2. Connection scale and sticky routing strategy.
3. Crash recovery with operation log + snapshot compaction.

## 6. Wrap-Up

- Re-state consistency guarantee as eventual convergence.
- Highlight failure behavior and what remains strongly durable.
