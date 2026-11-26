# Strong Answer: Distributed Unique ID Generator (Snowflake)

**Pacing Target:** 40 minutes

## 1. Introduction & Requirements (5 mins)
**Say:** "To generate highly scalable, 64-bit numerical IDs that are sortable by time and collision-free, I will implement a distributed ID generator based on the Snowflake algorithm. The system needs to support high throughput (over 10,000 IDs/sec/node) and low latency without a centralized bottleneck."

## 2. High-Level Architecture & Domain Model (Beginner / Core) (15 mins)
**Say:** "The core idea is to compose a 64-bit integer using bitwise operations: 1 sign bit set to 0, 41 bits for a custom epoch timestamp (giving us ~69 years), 10 bits for a dynamic Worker ID (allowing 1,024 nodes), and a 12-bit local sequence counter.
The architecture consists of an ID Generator Application running across multiple stateless nodes, and a ZooKeeper cluster used exclusively at startup to lease a unique 10-bit Worker ID."

## 3. Deep Dive: Clock Drift & Failure Trace (Core) (10 mins)
**Say:** "The most critical failure domain is clock drift. If the NTP daemon shifts the system clock backwards, we risk generating duplicate IDs.
**Concrete Failure Trace:** Suppose the clock is at 1005ms and shifts back to 1002ms. The local state machine detects `current_time < lastTimestamp`. To enforce our strict collision-free contract, the system will fail-fast or sleep. If the drift is minor, the thread sleeps until the clock catches up to 1005ms. If large, it throws a `ClockMovedBackwardsException` (503 Service Unavailable), sacrificing temporary availability for absolute consistency."

## 4. Optional Staff-Level Analysis (Staff) (5 mins)
**Say:** "At a staff level, we could mitigate the availability loss during backward shifts by 'borrowing' sequence numbers from the future, artificially advancing the logical timestamp if we haven't exhausted the sequence limits for those milliseconds. Furthermore, I'd ensure our API serializes the 64-bit integer as a string in JSON, protecting JavaScript clients from truncating IDs beyond 53 bits."

## 5. Wrap Up (5 mins)
**Say:** "By combining a decentralized bit-shifting generation strategy with ZooKeeper for node coordination, we achieve microsecond latency generation while robustly handling distributed clock anomalies."
