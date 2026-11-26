# Pitfalls: Key-Value Store

*   **Ignoring Vector Clock growth:** Vector clocks can grow large if many clients/nodes coordinate writes. Mitigation involves truncation or pruning strategies.
*   **Assuming Hinted Handoff is enough:** Hinted handoff only masks temporary failures. Persistent discrepancies require anti-entropy protocols like Merkle trees to reconcile replicas efficiently without full data transfers.
*   **LWW data loss:** Using Last-Write-Wins (LWW) with physical timestamps can lead to lost updates in a highly concurrent environment due to clock drift across nodes.
