# Digital Wallet & Transactional Ledger - Follow-Up Questions

## Follow-up questions

1. **Handling Hot Accounts:** How do you handle extreme write contention on a single "hot" account (e.g., a massive charity receiving thousands of small donations per second)?
2. **Reconciliation:** Your internal system is highly consistent, but you must interface with external legacy banking networks that process batches overnight. How do you design the reconciliation pipeline?
3. **Cross-Region Replication:** How do you adapt your Raft groups if the system must operate across three geographically dispersed data centers?

## Variants and extensions

- **Multi-Currency & Exchange:** Extending the system to support real-time currency exchange rates during transfers.
- **Crypto Wallet:** Modifying the ledger to support UTXO (Unspent Transaction Output) models for blockchain integration.
- **Micro-transactions / Gaming:** Optimizing the ledger for incredibly high volume, sub-cent transactions where eventual consistency (batched writes) might be permissible to save storage costs.

## Interviewer probes to prepare

- "Walk me through the exact sequence of events if the orchestrator node crashes immediately after sending the 'TRY' command to the source shard."
- "If a user initiates a transfer but their network drops before receiving the response, how do they safely resume without risking a double charge?"
- "With 1.7 TB of ledger data generated daily, what is your archival strategy, and how do you serve historical audit queries for transactions from 5 years ago?"
