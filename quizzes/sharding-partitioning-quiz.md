# Sharding and Partitioning Quiz

23 questions focused on relevant concepts.

Time: 20 minutes
Difficulty: Medium

---

## Section 1: Core Concepts (23)


### Question 1
What is the difference between Sharding and Partitioning?

A) They are completely synonymous and can be used interchangeably in all contexts.
B) Sharding typically refers to horizontal partitioning across multiple physical machines, while partitioning often refers to logical division within a single database instance.
C) Sharding applies only to NoSQL databases, while Partitioning applies only to relational databases.
D) Sharding divides data by columns (vertical), while Partitioning divides data by rows (horizontal).

### Question 2
Which of the following describes 'Vertical Partitioning'?

A) Splitting a table by moving certain columns (e.g., large text fields or BLOBs) into a separate table or database.
B) Splitting a table by moving certain rows to one database and other rows to another.
C) Replicating the entire database to a higher-tier, more powerful server.
D) Partitioning a database based on the time of day the data was created.

### Question 3
Which of the following is a key advantage of Range-based Sharding?

A) It eliminates the need for a routing tier or configuration server.
B) It naturally prevents hot shards by randomizing data placement.
C) It allows for efficient range queries (e.g., fetching all users between ID 1000 and 2000).
D) It is immune to unbalanced data growth over time.

### Question 4
What is the primary drawback of Hash-based Sharding?

A) It is only supported by NoSQL databases.
B) Range queries become very inefficient as contiguous data is randomly scattered across all shards.
C) It requires all queries to be broadcast to all shards.
D) It is impossible to add new shards once the database is deployed.

### Question 5
In a Directory-Based Sharding architecture, what is the role of the lookup service (directory)?

A) It performs background garbage collection on deleted records across shards.
B) It caches the results of frequent database queries to reduce load.
C) It enforces schema constraints and foreign keys across different shards.
D) It stores a mapping of which shard holds which specific data key or tenant.

### Question 6
What is the primary benefit of Consistent Hashing over traditional modulo hashing (key % N) when sharding a database?

A) It evenly distributes data exactly equally across all nodes at all times.
B) It minimizes data movement when adding or removing nodes from the cluster.
C) It completely eliminates the possibility of hot keys or hot shards.
D) It guarantees that all queries will run in O(1) time.

### Question 7
How do 'virtual nodes' (or vnodes) improve consistent hashing?

A) They allow consistent hashing to work without a hash function.
B) They encrypt the hash keys to prevent reverse-engineering of the hash ring.
C) They act as temporary backup nodes that only activate when a physical node fails.
D) They map a single physical server to multiple points on the hash ring, improving data distribution and load balancing.

### Question 8
What is a 'hot shard'?

A) A shard that has recently been rebooted and its cache is empty.
B) A shard that receives a disproportionately high amount of read/write traffic compared to others.
C) A shard dedicated exclusively to storing encrypted data.
D) A shard that is temporarily unavailable due to network partition.

### Question 9
What is 'Rebalancing' in a sharded cluster?

A) Restarting all nodes simultaneously to clear their memory caches.
B) The process of moving data between shards to ensure an even distribution of load and storage.
C) Switching the primary and replica roles during a failover event.
D) Updating the database schema across all shards to maintain consistency.

### Question 10
If you are sharding a multi-tenant SaaS application, what is the most logical sharding key to start with?

A) The Tenant ID (or Organization ID).
B) The timestamp of when the record was created.
C) The auto-incrementing integer ID of the specific row.
D) The email address of the user who created the record.

### Question 11
What is 'Scatter-Gather' querying?

A) A background process that consolidates fragmented data pages on disk.
B) A caching strategy that pre-fetches data from adjacent shards.
C) A query technique where the client connects directly to a random shard and hopes to find the data.
D) A query that does not include the sharding key, forcing the routing tier to send the query to all shards, gather the results, and merge them.

### Question 12
Why is Pagination (e.g., ORDER BY timestamp LIMIT 10 OFFSET 1000) problematic in a sharded environment without a shard key?

A) Because pagination syntax is not supported by distributed SQL engines.
B) Because shards will refuse to return more than 10 records at a time.
C) Because timestamps are never synchronized across different physical servers.
D) Because the routing tier must fetch (OFFSET + LIMIT) records from *every* shard, sort them all in memory, and then return the top 10.

### Question 13
Why are cross-shard joins typically avoided in distributed database architectures?

A) They are explicitly banned by the SQL standard for distributed systems.
B) They corrupt the index structures on the participating shards.
C) They require massive amounts of network bandwidth and scatter-gather processing, leading to high latency.
D) They always result in deadlocks if more than two shards are involved.

### Question 14
What is a common technique to mitigate the need for cross-shard joins?

A) Denormalization (e.g., duplicating related data into a single document or table on the same shard).
B) Switching from hash-based sharding to range-based sharding.
C) Using a Bloom filter on the application layer.
D) Increasing the CPU allocation of the database coordinator node.

### Question 15
What is the 'Celebrity Problem' in the context of sharding?

A) When the database administrator has too much access to user data.
B) When the cost of the database cluster becomes too high to justify.
C) When an extremely popular entity (e.g., a celebrity account) receives massive traffic, creating a hot shard regardless of the sharding strategy.
D) When highly sensitive VIP data must be stored on dedicated, isolated hardware.

### Question 16
How can you address the 'Celebrity Problem' for read-heavy workloads?

A) By caching the celebrity data heavily and potentially serving it from a CDN or distributed in-memory cache.
B) By implementing synchronous Write-Through caching.
C) By moving the celebrity data to a slower, high-capacity hard drive.
D) By changing the sharding strategy from hash to range.

### Question 17
In a geographically distributed database, what is 'geo-partitioning'?

A) Replicating the entire database to every region to ensure low latency everywhere.
B) Encrypting data differently based on the continent it was created in.
C) Partitioning data such that records are stored in the physical region closest to the user or where the data is legally required to reside.
D) Using GPS coordinates as the primary key for all database tables.

### Question 18
In a directory-based sharding setup, what happens if the directory service goes down?

A) The shards automatically elect a new directory service from among themselves.
B) The system falls back to traditional modulo hashing automatically.
C) Read queries continue working, but write queries fail.
D) The application cannot route queries to the correct shards, effectively causing a total cluster outage.

### Question 19
Which of these is a valid strategy for handling cross-shard transactions (ACID guarantees across shards)?

A) Read-Through Caching.
B) Bloom Filters.
C) Two-Phase Commit (2PC).
D) Consistent Hashing.

### Question 20
When performing a live cutover to a new sharded database using CDC (Change Data Capture), what is the typical sequence of events?

A) Take a snapshot and bulk load -> use CDC to apply ongoing changes -> switch application reads/writes when replication lag is near zero.
B) Start dual writes -> copy historical data -> stop dual writes.
C) Use CDC to copy historical data -> take a snapshot -> switch application reads/writes.
D) Stop the application -> copy data -> start the application on the new database.

### Question 21
When designing a distributed database cluster using Hash-based Sharding, how does the system typically handle adding a new node to the cluster without employing consistent hashing?

A) It transparently proxies queries to the new node while preserving the original modulo hashing layout.
B) It requires a full redistribution (rehashing) of nearly all existing data across all nodes, causing significant operational overhead and potential downtime.
C) It automatically transitions to Directory-based Sharding to map new data to the new node.
D) It relies on two-phase commit (2PC) to synchronously duplicate all writes to the new node until it is balanced.

### Question 22
Which of the following describes a key advantage of Directory-based Sharding over Hash-based Sharding?

A) It eliminates the need for any lookup mechanism, providing direct constant-time access to the correct node.
B) It allows for flexible and dynamic reassignment of specific keys or tenants to different shards without rehashing the entire dataset.
C) It automatically ensures zero replication lag and strict consistency across all distributed nodes.
D) It uses a deterministic modulo operation to distribute data, which inherently prevents hotspotting on individual nodes.

### Question 23
Why might a system designer choose to use a composite sharding key (e.g., `tenant_id` + `user_id`) instead of a single-column sharding key (e.g., `tenant_id` alone)?

A) To enforce a rigid maximum storage limit across all tenants automatically.
B) To distribute the data of extremely large tenants across multiple shards while keeping queries for specific users localized to a single shard.
C) To enable native cross-shard joins by ensuring all tables share at least one common sharding column.
D) To eliminate the need for a directory service in all sharding topologies.
