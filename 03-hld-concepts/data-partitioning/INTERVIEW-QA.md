# Interview Q&A: Data Partitioning

## 1) Why partition at all?
To keep per-node storage and throughput within limits while enabling horizontal scale.

## 2) Hash vs range partitioning?
Hash balances uniformly; range supports ordered access and locality.

## 3) What is a hotspot?
A partition receiving disproportionate traffic, causing latency and throttling.

## 4) How do you re-shard safely?
Dual-read/dual-write, incremental movement, verification, and rollback path.

## 5) Which projects use partitioning heavily?
- [URL Shortener](../../04-hld-projects/url-shortener/)
- [Chat Service](../../04-hld-projects/chat-service/)
- [News Feed](../../04-hld-projects/news-feed/)

## 6) How do you estimate the initial shard count?
Estimate logical bytes and peak operations per second separately, apply measured replication/index overhead and a utilization target, then choose the larger shard count with growth and skew headroom.

## 7) Why can `hash(key) % N` be painful to resize?
Changing `N` remaps most keys. Use a migration plan or a membership-aware scheme such as consistent/rendezvous hashing, and remember that hot keys still need separate treatment.
