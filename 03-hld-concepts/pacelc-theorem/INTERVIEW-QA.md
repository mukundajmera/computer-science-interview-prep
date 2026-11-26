# PACELC Theorem - Interview Q&A Scenarios

## 1. Financial Ledger - Account Balance
**Scenario:** A global banking application allows users to check their balance and transfer funds.
**Analysis:** You cannot risk double-spending. The system must choose **Consistency** over Availability during a partition, and **Consistency** over Latency during normal operations.
**PACELC Quadrant:** PC/EC.
**Tech Choice:** Google Spanner, CockroachDB.

## 2. E-commerce Shopping Cart
**Scenario:** Users adding items to a shopping cart during a major sale (e.g., Black Friday).
**Analysis:** If the system is down, you lose revenue. The system should remain available for writes even during a partition, and be fast during normal operation to prevent user drop-off. Occasional anomalies (e.g., deleted item reappears) are acceptable.
**PACELC Quadrant:** PA/EL.
**Tech Choice:** DynamoDB (eventual consistency), Cassandra.

## 3. Social Feed Counter (Likes/Views)
**Scenario:** Displaying the number of likes on a viral video.
**Analysis:** The exact number is not critical. Low latency and high availability are essential to handle massive read/write volumes.
**PACELC Quadrant:** PA/EL.
**Tech Choice:** Redis (async replication), Cassandra (ONE/LOCAL_ONE).

## 4. User Profile Settings (Password Update)
**Scenario:** A user updates their password.
**Analysis:** This is a low-frequency write but requires strong consistency so the user can immediately log in on any device. However, a brief unavailability during a severe partition is acceptable compared to letting them log in with an old password.
**PACELC Quadrant:** PC/EC.
**Tech Choice:** Relational database with synchronous replication.

## 5. IoT Sensor Data Ingestion
**Scenario:** Millions of sensors reporting temperature every second.
**Analysis:** Writes must be fast and highly available. Dropping a few data points or delaying them is fine, as long as the ingestion pipeline does not stall.
**PACELC Quadrant:** PA/EL.
**Tech Choice:** Apache Kafka, Cassandra.

## 6. Inventory Management for Rare Items
**Scenario:** Selling concert tickets where only 10 VIP seats are available.
**Analysis:** Overselling is unacceptable. You must guarantee strong consistency.
**PACELC Quadrant:** PC/EC.
**Tech Choice:** Redis (with Lua scripts for atomicity) or RDBMS with pessimistic locking.

## 7. Real-time Multiplayer Game State
**Scenario:** Tracking player positions in a fast-paced game.
**Analysis:** Latency must be extremely low. Stale data (a few milliseconds old) is corrected quickly.
**PACELC Quadrant:** PA/EL.
**Tech Choice:** UDP-based custom servers, Redis.

## 8. Collaborative Document Editing (Google Docs)
**Scenario:** Multiple users typing in a document simultaneously.
**Analysis:** Local writes must be fast (low latency), but eventual consistency across clients is resolved via Operational Transformation or CRDTs. It falls into PA/EL but with complex conflict resolution.
**PACELC Quadrant:** PA/EL.
**Tech Choice:** Custom backend with WebSockets and CRDTs.

## 9. Content Delivery Network (CDN) Configuration Updates
**Scenario:** Updating caching rules globally.
**Analysis:** It's acceptable for different regions to see the old rules for a few minutes, but the control plane should remain available and fast.
**PACELC Quadrant:** PA/EL.
**Tech Choice:** Distributed key-value store with eventual consistency.

## 10. Audit Logging System
**Scenario:** Storing compliance logs that must never be lost.
**Analysis:** Writes must be highly durable and consistent. If a partition occurs, it might be better to buffer locally or halt than to lose data. Under normal operations, we might accept slight latency to ensure it's written safely.
**PACELC Quadrant:** PC/EC or PC/EL.
**Tech Choice:** Kafka (with acks=all).
