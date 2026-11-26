# Multi-Region Active-Active — Strong Answer

## 60-90 Second Wrap-Up

**Say:** "To achieve sub-50ms latency for a globally distributed user base while surviving regional outages, we implemented a multi-region active-active architecture."

**Say:** "Traffic is routed to the closest healthy region using Anycast BGP, allowing immediate, network-level failover without DNS propagation delays."

**Say:** "To keep write latency low, we accept writes locally in each region and replicate them asynchronously. We explicitly trade strict consistency for availability and speed, resolving concurrent cross-region writes using Last-Write-Wins powered by Hybrid Logical Clocks."

**Say:** "To ensure a seamless user experience, we maintain read-after-write consistency by passing version tokens to the client. If a network partition occurs, regions operate independently, relying on durable replication queues and background anti-entropy processes to reconcile data safely once connectivity is restored."
