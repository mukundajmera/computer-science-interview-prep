# Brokerage Platform — Comparison

## Brokerage vs Distributed Cache

| Concern | Brokerage | Distributed Cache |
|---|---|---|
| Correctness target | Strong for order state | Eventual acceptable for many workloads |
| Core write path | Stateful workflow commands | Key-value mutations |
| Failure recovery | Reconciliation with external system | Replica repair/rebalance |

## Brokerage vs Ride Sharing

| Concern | Brokerage | Ride Sharing |
|---|---|---|
| Realtime stream | Symbol prices and order events | Driver location and trip events |
| Hot path guarantee | Financial consistency | Assignment correctness + latency |
| External dependency | Exchange adapters | Mapping and geo services |

## Brokerage vs Video Streaming

| Concern | Brokerage | Video Streaming |
|---|---|---|
| Dominant load | Bidirectional realtime + command writes | Heavy read streaming and blob processing |
| Stateful workflow | Order lifecycle | Upload/transcode lifecycle |
| Consistency posture | Strong command correctness | Availability-first playback |
