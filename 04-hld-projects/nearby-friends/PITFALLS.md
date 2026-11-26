# Nearby Friends - Common Pitfalls

## 1. Designing a P2P architecture for mobile
- **Failure Signal:** The candidate suggests phones open direct connections to each other to share locations.
- **Root Cause:** Treating mobile devices like data center servers, ignoring NAT traversal, battery sleep states, and cellular network firewalls.
- **Mitigation:** Firmly state constraints around mobile battery life and connectivity. Centralize connections via cloud WebSockets.
- **Validation:** Ensure the architecture diagram routes all mobile traffic through a centralized gateway/server layer.

## 2. Using Geohash channels for a "Friends Only" feature
- **Failure Signal:** The candidate insists on partitioning the Pub/Sub system by geographic grids (Geohashes) instead of user IDs.
- **Root Cause:** Blindly applying a general "location-based service" pattern without recognizing that this feature is strictly constrained by the *social graph*.
- **Mitigation:** Clarify that if a user subscribes to a Geohash, they receive updates for *everyone* in that grid, wasting bandwidth filtering out non-friends.
- **Validation:** Check the channel naming convention; it should be user-centric (e.g., `channel:user_id`).

## 3. Ignoring the fan-out multiplier
- **Failure Signal:** Designing the system based solely on the ingest QPS ($334,000/s$) and sizing databases accordingly, while ignoring the $14\text{M}/s$ outbound push rate.
- **Root Cause:** Overlooking that one write (location update) results in $N$ reads/pushes (online friends).
- **Mitigation:** Force the candidate to explicitly calculate the read-to-write ratio during the estimation phase.
- **Validation:** Review the sizing math. The Pub/Sub or message bus layer must be sized for the $14\text{M}/s$ throughput.

## 4. Using a heavy RDBMS or Kafka for ephemeral real-time state
- **Failure Signal:** Attempting to read/write real-time 30-second location updates directly from/to PostgreSQL or using Kafka to route messages to WebSockets.
- **Root Cause:** Misunderstanding the latency requirements and ephemeral nature of the "currently online" state. Kafka is durable and slower; RDBMS cannot handle the $334\text{k}/s$ writes efficiently without heavy sharding.
- **Mitigation:** Separate the architecture into a real-time ephemeral path (Redis cache + Pub/Sub) and an async durable path (Cassandra).
- **Validation:** Verify two distinct storage sinks in the design diagram.