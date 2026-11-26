# 🏆 Coach Answer: Payment System — LLD

> **Type:** Low-Level Design
> **Difficulty:** Advanced
> **Time Target:** 45 minutes

## Core focus
This solution focuses on correct idempotent intent creation, robust state machine transitions, and safe asynchronous webhook reconciliation to tolerate duplicated or out-of-order gateway callbacks.

## Reference implementation
- **[Payment System - Strong Answer](../02-lld-projects/payment-system/STRONG-ANSWER.md)**
- **[Approach & Code Walkthrough](../02-lld-projects/payment-system/CODE-WALKTHROUGH.md)**

## Evaluation points
1. **Idempotency Model**: Can the system reject identical keys with mismatched payloads to prevent double charging?
2. **Reconciliation Logic**: Does the system safely handle ambiguous timeouts and retry webhooks out-of-order without violating terminal states?
3. **Concurrency**: Are multi-step mutations protected by proper locks or optimistic concurrency controls in the target language?
