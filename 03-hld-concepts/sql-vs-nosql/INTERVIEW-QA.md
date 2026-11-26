# Interview Q&A: SQL vs NoSQL

## 1) Is SQL better than NoSQL?
Neither is universally better. Choose based on consistency, query complexity, and scale profile.

## 2) When is SQL mandatory?
When strict transactional correctness across related entities is non-negotiable.

## 3) When is NoSQL clearly better?
When high-scale partitioned workloads with simple access paths dominate.

## 4) What is polyglot persistence?
Using multiple data stores in one system based on bounded context and workload.

## 5) How do you migrate from SQL to NoSQL safely?
Use dual-writes, backfill, consistency checks, and gradual traffic cutover.

## 6) Which projects show this trade-off?
- [Chat Service](../../04-hld-projects/chat-service/)
- [News Feed](../../04-hld-projects/news-feed/)
- [Ecommerce Backend](../../04-hld-projects/ecommerce-backend/)

## 7) Does choosing NoSQL automatically solve scale or availability?
No. Partition-key skew, hot keys, replication settings, consistency mode, and operational limits still determine behavior; validate the specific engine and topology.

## 8) What should a first capacity estimate include?
Convert daily volume to average and peak QPS, estimate retained raw bytes, then account for indexes, replicas, compaction, hot-key skew, and recovery headroom before comparing candidate designs.
