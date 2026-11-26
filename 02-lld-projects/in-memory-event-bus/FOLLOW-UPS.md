# In-Memory Event Bus - Follow-Ups

*Note: The following are optional, unimplemented extensions not covered by the current codebase.*

- **Disk Persistence**: How to persist events to an append-only log on disk for durability? (Requires moving away from purely in-memory data structures).
- **Distributed Coordination**: How to make the event bus distributed across multiple nodes? (Requires consensus protocols like Raft or external coordination like ZooKeeper).
- **Exactly-Once Semantics**: How to support exactly-once processing semantics? (Requires idempotent consumers and transactional producers).
