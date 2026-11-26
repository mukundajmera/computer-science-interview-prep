# Comparison: Key-Value Store Technologies

| Feature | Dynamo (Amazon) | Cassandra (Apache) | Riak | Redis Cluster |
|---|---|---|---|---|
| **Architecture** | Masterless ring | Masterless ring | Masterless ring | Master-Slave with sharding |
| **Consistency** | Tunable (Eventual) | Tunable (Eventual) | Tunable (Eventual) | Strong (Single-key) |
| **Storage Engine** | Pluggable | LSM-tree | Pluggable | In-memory |
