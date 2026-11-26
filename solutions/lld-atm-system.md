# 🏆 Coach Answer: ATM System — LLD

> **Type:** Low-Level Design  
> **Difficulty:** Intermediate/Hard  
> **Time Target:** 45 minutes

---

## Canonical Interview Answer

This project has a definitive canonical interview answer that thoroughly explains the state pattern design, entity modeling, thread-safety, correctness boundaries, and failure scenarios.

Please refer to the full canonical answer here:
[ATM System - Strong Answer](../02-lld-projects/atm-system/STRONG-ANSWER.md)

---

## Key Takeaways

1. **State Management**: The State pattern is pivotal. It strictly controls the lifecycle from inserting a card, authenticating a PIN, selecting a transaction, and dispensing cash, preventing out-of-order errors.
2. **Concurrency and Transfer Consistency**: Concurrent operations require meticulous handling. Concurrent opposite-direction transfers preserve total account money and never overdraw; locks use a collision-free stable total account-ID order.
3. **Failure Cases**: Physical and network edge cases must be handled explicitly. Capacity bounds (cash inventory shortage) are checked before processing, duplicate operation IDs manage network retries, and positive-amount checks ensure data integrity.
