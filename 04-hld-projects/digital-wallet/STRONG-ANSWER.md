# Digital Wallet & Transactional Ledger - Strong Answer

## Introduction

> Say: "To support 50,000 peak TPS for a digital wallet, we cannot rely on a traditional monolithic RDBMS using 2-Phase Commit. The cross-node lock contention would crush our throughput to under 3,000 TPS. Instead, we must shard the accounts and use Event Sourcing backed by Raft consensus for high-throughput, lock-free writes."

## Handling Distributed Transactions

> Say: "For transactions crossing two different shards, we will use a Try-Confirm/Cancel pattern. To guarantee we never artificially create money during a partial failure or network timeout, we establish a strict symmetrical invariant: both the source and destination shards must successfully complete the TRY phase (reserving funds and validating state) before any CONFIRM is sent to either shard. This prevents money duplication if a destination credit succeeds but the network response drops."

## Auditability and Recovery

> Say: "Because financial correctness is paramount, the materialized `accounts` table is not our source of truth. Our source of truth is the immutable Write-Ahead Log of ledger entries. If the account state is ever corrupted or lost, we can completely rebuild the exact financial state to the penny by replaying the event log."

## Idempotency

> Say: "At this scale, network retries are guaranteed. We will mandate an `idempotency_key` on all mutation APIs, caching it in a fast key-value store like Redis to reject duplicate inflight requests immediately, while also persisting it in the ledger log to prevent long-term double-spending."
