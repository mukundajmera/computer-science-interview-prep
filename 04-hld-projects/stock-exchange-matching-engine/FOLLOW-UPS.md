# Stock Exchange Matching Engine - Follow-Up Questions

## Follow-up questions

1. **How do you handle a slow consumer of market data?**
   - If you are publishing UDP multicast, the network handles it. If using TCP, the OS buffer will fill, eventually blocking the publisher if not handled. The publisher must use non-blocking I/O, drop packets for slow consumers, or disconnect them to protect the matching engine.

2. **How do you perform end-of-day reconciliation?**
   - The persisted sequenced event log is replayed against a fresh engine instance to ensure the final state matches the primary engine's memory snapshot.

3. **What happens if the Sequencer goes down?**
   - The Sequencer is a single point of failure. It must be a highly available cluster (e.g., using Raft consensus) to elect a new leader and resume sequence ID generation without skipping or duplicating IDs.

## Variants and extensions

- **Crypto Exchange:** Add wallet management, blockchain confirmation delays, and handle massive amounts of retail WebSocket connections compared to a few FIX institutional connections.
- **Dark Pool:** Remove the Market Data publisher. The order book is entirely hidden.

## Interviewer probes to prepare

- "If the primary engine crashes immediately after matching an order but before sending the execution report, how does the standby know what to do?" (Answer: The standby is already processing the same input sequence. It will generate the exact same match and send the report).
