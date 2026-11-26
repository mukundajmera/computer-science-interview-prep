# HLD Projects Flashcards

40 question-only flashcards covering key system design projects and architectures.

---

## Social & Communication (Cards 1-8)

### Card 1
Front: What are the key trade-offs between fanout-on-write and fanout-on-read in a News Feed architecture?

### Card 2
Front: How do you maintain persistent connections and efficiently route messages in a distributed Chat Service?

### Card 3
Front: What data model and read-path optimizations are used in a Social Graph Engine (e.g., TAO) to serve highly concurrent connection queries?

### Card 4
Front: How do you handle real-time conflict resolution in a Collaborative Document Editor using OT or CRDTs?

### Card 5
Front: What is the optimal architecture for broadcasting Live Comments to millions of concurrent viewers during a live event?

### Card 6
Front: How do you design a Notification Service to ensure reliable delivery and avoid duplicate notifications across Email, SMS, and Push?

### Card 7
Front: How does a Nearby Friends system efficiently update and query high-frequency ephemeral location data?

### Card 8
Front: What is the recommended strategy for asynchronously processing and filtering user uploads in a Content Moderation platform?

## Data & Storage Systems (Cards 9-16)

### Card 9
Front: How do you prevent hash collisions and ensure scalability when generating unique identifiers for a URL Shortener?

### Card 10
Front: What is the role of a metadata database versus blob storage nodes in a Distributed Cloud Storage (S3) architecture?

### Card 11
Front: How do you manage data replication and consistent hashing in a Distributed Cache?

### Card 12
Front: What is the most efficient storage strategy for handling expiration and cleanup in a Pastebin-like text storage service?

### Card 13
Front: How do you architect a Distributed Object Storage system to handle massive file uploads using multipart upload?

### Card 14
Front: What are the main challenges in maintaining cross-region replication in a Multi-Region Active-Active database deployment?

### Card 15
Front: How do you structure a distributed inverted index to enable low-latency Social Post Search?

### Card 16
Front: How does a Kafka Distributed Broker handle partition replication and consumer group offsets?

## Streaming, Metrics, & Analytics (Cards 17-24)

### Card 17
Front: How do you implement chunking, transcoding, and adaptive bitrate streaming in a Video Streaming platform?

### Card 18
Front: What pipeline architecture is required to serve real-time personalized Video Recommendations at scale?

### Card 19
Front: How do you handle high-throughput event ingestion and real-time aggregations in an Ad Click Aggregator?

### Card 20
Front: What storage engine optimizations are necessary for a Metrics Monitoring system handling high-cardinality time-series data?

### Card 21
Front: How do you architect a Realtime Metrics Platform using tumbling windows and approximate counting algorithms?

### Card 22
Front: What stream processing techniques are used in a Bot Detection Platform to analyze traffic patterns with minimal latency?

### Card 23
Front: How do you inject and propagate trace IDs across microservices in a Distributed Tracing system?

### Card 24
Front: What is the system design for a Price Tracking Service that must continuously scrape and alert on millions of dynamic items?

## Commerce, Transactions, & Booking (Cards 25-32)

### Card 25
Front: How do you achieve idempotency and exactly-once processing in a Payment System architecture?

### Card 26
Front: What database properties and transaction models are required to safely transfer funds in a Digital Wallet system?

### Card 27
Front: How do you handle high-concurrency reservations and prevent double-booking in a Ticketing Platform?

### Card 28
Front: What is the architecture for an Online Auction system that requires strict bid consistency and real-time client updates?

### Card 29
Front: How do you build an ultra-low latency in-memory order book for a Stock Exchange Matching Engine?

### Card 30
Front: What asynchronous patterns are used in a Brokerage Platform to execute trades and reconcile ledger balances?

### Card 31
Front: How does an E-commerce Backend handle shopping cart state and distributed inventory decrements during checkout?

### Card 32
Front: How do you design a Distributed Job Scheduler to guarantee fault-tolerant execution of delayed and cron-based jobs?

## Location-Based & Routing Systems (Cards 33-40)

### Card 33
Front: How do you use Geohash or Quadtree indexes to efficiently query points of interest in a Proximity Service?

### Card 34
Front: What is the system architecture for matching riders and drivers in a Ride Sharing application?

### Card 35
Front: How do you model road networks and perform hierarchical routing in a Google Maps-like system?

### Card 36
Front: What algorithms and caching layers are needed to build a fast, distributed Search Autocomplete service?

### Card 37
Front: How do you manage rate limits and deduplication effectively in a massive-scale Web Crawler?

### Card 38
Front: What system design patterns are used to optimize hyper-local driver assignment in Quick Commerce Delivery?

### Card 39
Front: How do you manage complex task dependencies and state transitions in a Distributed Workflow Orchestrator?

### Card 40
Front: How do you scale a Realtime Gaming Leaderboard using Redis Sorted Sets and sharded ranking trees?
