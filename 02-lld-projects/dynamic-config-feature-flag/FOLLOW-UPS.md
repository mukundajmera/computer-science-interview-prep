# Follow-ups: Dynamic Configuration & Feature Flag Service

## 1. Multi-Node Deployment
**Question:** The current implementation is an in-memory Singleton, which works perfectly for a single server. How would you scale this to work across a cluster of hundreds of microservice instances?
**Target Answer:**
*   **Central Store:** Store the master configuration in a distributed key-value store (like Redis, ZooKeeper, or etcd).
*   **Local Caching:** Each application instance still maintains its in-memory `FeatureFlagManager` to ensure zero-latency reads.
*   **Sync Mechanism:**
    *   *Polling:* Background thread polls the central store every X seconds for changes.
    *   *Push (Pub/Sub):* The central store emits an event (e.g., via Redis Pub/Sub) when a flag changes. Instances listen to this channel and update their local cache immediately.

## 2. Bootstrapping and Resilience
**Question:** If the application starts up, and the central Redis server is down, how do you prevent the application from failing to boot or serving incorrect configurations?
**Target Answer:**
*   **Local File Fallback:** Upon successfully fetching configurations from Redis, the service dumps a snapshot of the flags to a local JSON file.
*   On subsequent restarts, if Redis is unreachable, the system reads from the local file snapshot as a fallback. If that fails, it relies entirely on the hardcoded `defaultValue` provided in the code.

## 3. Flag Lifecycle & Tech Debt
**Question:** Over time, old feature flags accumulate in the codebase, leading to "if-else" hell and tech debt. How do you design the system or processes to handle flag cleanup?
**Target Answer:**
*   **Telemetry:** The service should emit metrics every time a flag is evaluated. This allows dashboards to show "stale" flags that are either 100% ON or 100% OFF for a long time.
*   **Metadata:** Flag definitions should include an owner and a planned `expirationDate`.
*   **Code Scanning:** CI/CD tools can scan the codebase for flag keys that have been retired from the management UI.

## 4. Complex Targeting (Sticky Sessions)
**Question:** How would you handle a scenario where an anonymous user (no `userId`) needs consistent percentage rollout behavior during their session, but we later learn their `userId` when they log in?
**Target Answer:**
*   Use a session ID or device ID cookie generated on the client side for anonymous hashing.
*   Upon login, the system needs a deterministic way to prioritize identifiers (e.g., if logged in, always use `userId`, else use `deviceId`).
