# 🏆 Coach Answer: Ad Click Aggregator — HLD

> **Type:** High-Level Design
> **Difficulty:** Advanced
> **Time Target:** 45 minutes

## Requirements
- Clarify FR/NFR and hard constraints.
- Define explicit out-of-scope boundaries.

## Capacity assumptions
- Start with one envelope that forces architecture choices.
- Use burst factor and retention tiers.

## Core design
- API + idempotency contract first.
- Metadata store + durable log + worker pipeline.
- Query-optimized serving path for dashboard/read APIs.

## Deep dives
1. Correctness under retries and replay.
2. Hotspot/cardinality controls.
3. Cost-aware retention strategy.

## Wrap-up
- Summarize deliberate trade-off and 10x evolution path.
