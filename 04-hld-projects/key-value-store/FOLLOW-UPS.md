# Follow-Ups: Key-Value Store

1.  **How do you handle hot keys?**
    *   *Answer:* Introduce an caching layer or perform local caching on the coordinator node if traffic is extremely skewed.
2.  **How do you scale out the system?**
    *   *Answer:* Add nodes. They gossip their presence, take over a subset of vnodes on the hash ring, and stream data from existing replicas.
