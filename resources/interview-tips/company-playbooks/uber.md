# Uber L5/L6 Interview Playbook

Uber's engineering challenges are uniquely grounded in the physical world. The core of their business involves matching moving objects (riders and drivers) in real-time on a planetary scale. The interview process for senior (L5) and staff (L6) roles focuses heavily on real-time dispatch systems, geospatial indexing, stateful services, and event-driven architectures. This playbook explores the leveling rubrics, the H3 geospatial index, Ringpop for application sharding, and the use of Kafka for massive data pipelines.

## L5/L6 Leveling Rubrics

Uber's leveling system differentiates heavily between independent execution and architectural leadership in high-stakes, real-time environments.

At the L5 (Senior Software Engineer) level, candidates are expected to design and build complex, highly concurrent systems. They must handle ambiguity, make pragmatic architectural trade-offs, and deeply understand the operational characteristics of their services (latency, throughput, consistency). In interviews, an L5 candidate must demonstrate proficiency in distributed systems design, particularly concerning stateful workloads and data consistency.

At the L6 (Staff Software Engineer) level, the focus shifts to cross-domain leadership and architecting foundational platforms. An L6 engineer solves problems that impact multiple teams, such as designing a new routing algorithm or revamping the global messaging infrastructure. During interviews, L6 candidates are evaluated on their ability to design systems that handle massive scale, resolve complex failure modes (like network partitions in a dispatch system), and establish engineering standards for reliability and performance.

### Rubric Matrix

| Attribute | L5 Expectations | L6 Expectations |
| :--- | :--- | :--- |
| **System Design** | Architects robust, real-time services. Understands trade-offs between consistency and latency. | Designs foundational, org-wide platforms. Navigates complex distributed systems challenges (e.g., global state synchronization). |
| **Execution** | Independently delivers complex projects. Owns service reliability. | Drives major technical initiatives across multiple teams. Mentors senior engineers. |
| **Domain Expertise** | Deep understanding of concurrency and stateful services. | Mastery of complex domains like geospatial routing or planetary-scale event streaming. |
| **Impact** | Solves ambiguous problems within their specific product area. | Identifies and solves foundational architectural bottlenecks that impact the entire company. |

## Geospatial Indexing (H3)

Geospatial data is the lifeblood of Uber. Understanding how to index and query this data efficiently is paramount.

Uber developed and open-sourced H3, a hexagonal hierarchical spatial index. Unlike traditional grid systems or Geohashes, hexagons have equidistant neighbors, making radius queries and smoothing algorithms much more efficient.

In a system design interview, when asked to design a service that finds nearby drivers, you must discuss geospatial indexing. You should explain how a driver's raw GPS coordinates are converted into an H3 index (a hexagon ID). The backend can then query a database or cache for all drivers currently residing in that hexagon and its immediate neighbors, dramatically reducing the search space from a global scan to a localized lookup.

## Real-Time Ride Dispatch

The core Uber dispatch system is incredibly complex, requiring low latency, high availability, and strong consistency (to ensure a driver isn't assigned to two riders simultaneously).

Designing this system requires understanding stateful services. Drivers constantly stream their location updates. You must architect a system that ingests this massive firehose of telemetry data, updates the geospatial index in real-time, and runs matching algorithms (like bipartite matching) to pair riders and drivers optimally.

You must discuss how to handle concurrent requests and maintain state without overwhelming a central database, often utilizing in-memory data grids or distributed caches.

## Ringpop and Consistent Hashing

Managing stateful, real-time connections (like WebSockets from millions of driver apps) requires sophisticated application-layer sharding.

Uber developed Ringpop to solve this. Ringpop provides a decentralized, highly available application-layer sharding mechanism based on consistent hashing and a gossip protocol (SWIM). 

In an interview, you should explain how to route a rider's request to the specific backend server that currently holds the state of the matched driver. Discussing consistent hashing demonstrates you understand how to distribute load evenly and minimize cache invalidation when servers are added or removed from the cluster.

## Kafka Planetary Messaging

Uber generates a staggering amount of data (location updates, trip events, analytics). They rely on Apache Kafka as the central nervous system for asynchronous communication.

You must understand how to design event-driven architectures using Kafka. For example, when a trip is completed, a "TripFinished" event is published to a Kafka topic. Multiple downstream services (billing, analytics, driver ratings) consume this event asynchronously. 

Interviewers look for candidates who understand Kafka's partitioning model, how consumer groups work, and the trade-offs between at-least-once, at-most-once, and exactly-once delivery semantics in high-throughput pipelines.

## Concrete Interview Scenarios

### Scenario: Design Uber Surge Pricing
**Interviewer:** "Design the backend system that calculates and applies surge pricing in real-time."

**Candidate Approach (L5):**
The candidate designs a data pipeline. They propose using Kafka to ingest rider app opens (demand) and driver locations (supply). They use a stream processing framework (like Apache Flink) to aggregate this data into time windows grouped by H3 hexagons. They design a pricing service that reads these aggregations, applies a pricing algorithm, and caches the resulting surge multiplier in Redis for low-latency retrieval by the rider app.

**Candidate Approach (L6):**
The L6 candidate expands on this by addressing global state and extreme edge cases. They discuss how to handle "thundering herds" when a concert ends, proposing techniques to smooth out demand spikes. They dive deep into the consistency requirements of the pricing algorithm—what happens if the pricing service fails mid-calculation? They also design the feedback loop, analyzing how a surge price actually affects demand in real-time, and adjusting the algorithm dynamically.

### Sample Answer: Handling Driver Location Updates
**Question:** "Drivers send location updates every 4 seconds. How do you design a system to ingest and store this data without crashing the database?"

**Sample Answer:** "Writing every location ping directly to a persistent database like Cassandra would overwhelm it with write IOPS. Instead, I would ingest the pings via an API Gateway and place them onto a partitioned Kafka topic. A stream processing layer would consume these events, updating an in-memory cache (like Redis) that serves the real-time dispatch queries. To persist the data for analytics, the stream processor would batch the location updates over a longer time window (e.g., 1 minute) and asynchronously write those batches to the persistent database, drastically reducing the write load while maintaining real-time availability for the core business logic."

## Conclusion

Interviewing at Uber requires a shift in mindset from traditional CRUD applications to real-time, stateful, and event-driven architectures. By demonstrating mastery of geospatial concepts like H3, application sharding, and robust data pipelines using Kafka, you will show that you are capable of engineering systems that orchestrate the physical movement of millions of people worldwide.
