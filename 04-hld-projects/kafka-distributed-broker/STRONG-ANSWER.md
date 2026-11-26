# Strong Answer

**Say:** "I will architect this as a distributed commit log rather than a traditional message queue. By making the log append-only and partitioning it across multiple brokers, we can sustain 5M events per second while relying on the OS page cache for low-latency delivery."

**Say:** "For high availability, we will replicate partitions using an In-Sync Replica (ISR) model. The leader handles all reads and writes for a partition, and followers fetch data to stay in sync. This provides strong durability without the latency penalty of full quorum consensus on every write."

**Say:** "Consumers will pull data using offsets rather than the broker pushing messages. This shifts the tracking burden to the consumer groups, preventing slow consumers from applying backpressure to the cluster and allowing replayability."
