# Chat/Messaging Service - Follow-Up Questions

Common follow-ups after the baseline chat design.

> Related docs: [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [PITFALLS](./PITFALLS.md) · [STRONG-ANSWER](./STRONG-ANSWER.md)

## 1. What happens if the WebSocket connection drops frequently?

- Use heartbeat + reconnect backoff.
- Require replay cursor and idempotent client send IDs.
- Add duplicate suppression and gap detection metrics.

## 2. How do you handle message ordering under concurrent sends?

- Guarantee ordering per conversation partition.
- Use ordering IDs, not only wall-clock timestamps.
- Define conflict/tie-break behavior for simultaneous events.

## 3. How do you handle presence-store degradation (for example Redis outage)?

- Fail to queue-first delivery mode, not message loss.
- Defer non-critical presence updates and recover asynchronously.
- Keep explicit degraded-state telemetry and alerting.

## 4. How do you support multi-device sync correctly?

- Track sessions by device.
- Maintain device-level read cursors.
- Broadcast read-sync and message edits/deletes across active devices.

## 5. How do you scale group messaging to very large groups?

- Switch to hybrid fan-out policy based on group size/activity.
- Use topic-like delivery channels and pull-based catch-up where needed.
- Throttle non-critical events (typing/presence) in large groups.

## 6. How do you add disappearing messages?

- Add TTL semantics at message level.
- Support server-side cleanup and client-side expiry behavior.
- Clarify guarantees and non-goals (for example screenshots).

## 7. How do you add message search?

- Without E2E: index via async pipeline.
- With E2E: move search to client or encrypted-search constraints.
- Keep search indexing outside hot send path.

## 8. How do you add voice/video calling?

- Reuse messaging channel for signaling.
- Use dedicated media path (WebRTC/SFU) for media plane.
- Keep call state and message state decoupled.

## 9. How do you expose last-seen while respecting privacy rules?

- Model privacy policy at read-time and publish-time.
- Cache policy decisions carefully to avoid stale leaks.
- Define audit and override behavior for compliance needs.

## 10. What changes for multi-region active-active?

- Region-local writes with bounded cross-region convergence.
- Explicit conflict resolution and replay strategy.
- Disaster recovery plan with user-visible consistency expectations.

## 11. How do you handle Tinder-like mutual match notifications reliably?

- Persist swipe intent idempotently before inverse-like lookup.
- Use deterministic pair keys to avoid double/missed match races.
- Emit match events via durable queue for notification fan-out.
