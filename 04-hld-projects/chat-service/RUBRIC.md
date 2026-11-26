# Chat/Messaging Service - Interview Scoring Rubric

Use this rubric to evaluate a WhatsApp-like chat design answer across seven dimensions.

> Related docs: [PROBLEM](./PROBLEM.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

## Scoring overview

| # | Dimension | Weight | Core signal |
|---|---|---|---|
| 1 | Requirements and scope | 10% | Correctly bounds core chat vs out-of-scope |
| 2 | Capacity and constraints | 10% | Numbers justify architecture choices |
| 3 | API/interface design | 15% | Clear REST + realtime contract |
| 4 | Data model | 15% | Correct storage split by consistency and access path |
| 5 | Architecture | 20% | End-to-end write/read/replay flow |
| 6 | Deep dives | 20% | Ordering, reconnect, multi-device, failure handling |
| 7 | Trade-offs and communication | 10% | Clear alternatives and decisions |

## 1. Requirements and scope

| Score | Descriptor |
|---|---|
| 1 | Jumps into components without clarifying group size, offline horizon, or latency SLOs. |
| 3 | Clarifies core features and one or two NFRs; partially defines boundaries. |
| 5 | Explicitly clarifies group limits, offline retention, multi-device behavior, last-seen privacy, and out-of-scope items. |

## 2. Capacity and constraints

| Score | Descriptor |
|---|---|
| 1 | No concrete numbers. |
| 3 | Provides rough QPS and storage estimates but misses connection scale implications. |
| 5 | Derives message QPS, connection count, storage growth, and uses them to justify queueing, store choice, and connection tier sizing. |

## 3. API/interface design

| Score | Descriptor |
|---|---|
| 1 | REST-only CRUD with no realtime semantics. |
| 3 | Includes basic send/read endpoints and simple websocket events. |
| 5 | Defines idempotent send contract, reconnect replay token/cursor, ack semantics, and failure/error behavior. |

## 4. Data model

| Score | Descriptor |
|---|---|
| 1 | Single-table handwave. |
| 3 | Reasonable message store with presence cache. |
| 5 | Clean split: durable message store, ephemeral presence/session store, and metadata store with clear partition/access patterns. |

## 5. Architecture

| Score | Descriptor |
|---|---|
| 1 | Generic boxes with no path details. |
| 3 | Basic publish/deliver flow. |
| 5 | Full path: persist -> queue -> online push/offline backlog -> replay on reconnect, with group fan-out and push fallback. |

## 6. Deep dives (WhatsApp-specific)

| Score | Descriptor |
|---|---|
| 1 | Skips failure mode discussion. |
| 3 | Covers one or two deep dives. |
| 5 | Handles all: websocket disconnect/reconnect replay, Redis/presence degradation plan, out-of-order mitigation, multi-device cursor sync, and last-seen privacy controls. |

## 7. Trade-offs and communication

| Score | Descriptor |
|---|---|
| 1 | Tool-name listing without decisions. |
| 3 | Some trade-offs but weak decision rationale. |
| 5 | Explicitly compares options (WebSocket vs fallback, strict vs eventual consistency, per-message vs batched receipts) and states why each choice fits product constraints. |

## Calibration guide

| Total (out of 35) | Rating |
|---|---|
| 30-35 | Strong hire signal |
| 22-29 | Hire |
| 15-21 | Mixed/lean no-hire |
| 7-14 | No-hire signal |
