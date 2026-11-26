# Nearby Friends - Strong Answer

## Summary of a Strong Interview Performance

A strong answer for "Nearby Friends" immediately recognizes the tension between mobile constraints and massive fan-out requirements.

**1. Scoping and Constraints:**
**Say:** "This feature is battery and network intensive. We cannot use a peer-to-peer model because keeping radio antennas awake constantly will destroy mobile battery life. Furthermore, we must strictly limit data transfer. Therefore, I will design a centralized system where clients send updates every 30 seconds, and the server pushes updates *only* for friends who are currently online and within a 5-mile radius."

**2. Identifying the Bottleneck:**
**Say:** "Let's look at the math. With $10\text{M}$ concurrent users updating every 30 seconds, we have an ingest rate of about $334,000\text{ QPS}$. That's high, but easily handled by a horizontally scaled API tier. The real bottleneck is the fan-out. If an average user has 400 friends and 10% are online, every incoming update needs to be pushed to 40 other users. That means our internal routing system must handle $334,000 \times 40 \approx 14\text{ Million}$ messages per second. I need to design for that specific choke point."

**3. Architecture & Protocols:**
**Say:** "I'll use WebSockets for the client-server connection. It's full-duplex, meaning clients can push their 30s updates and receive friend updates over the same low-overhead TCP connection. 

Behind the WebSocket servers, I'll use a Redis Pub/Sub cluster. When User A comes online, their WebSocket server subscribes them to the channels of all their friends (e.g., `channel:user:{friend_id}`). When a friend sends a location update, their connected WebSocket server publishes the coordinate to that friend's channel. The Redis cluster routes it to User A's server, which calculates the distance, confirms it is under 5 miles, and pushes it down the socket to User A."

**4. State Management:**
**Say:** "We need to separate real-time state from historical analytics. 
For real-time, I'll use a Redis Key-Value cache storing `{lat, lng, timestamp}` with a 10-minute TTL. This handles the 'inactive friend drop-off' requirement automatically. When a user first opens the app, we query this cache to get the initial map state.
For historical analytics, I will not put that on the critical real-time path. Instead, the WebSocket server will drop a copy of the incoming location event onto a Kafka topic. Asynchronous workers will consume this topic and batch-write to a Cassandra wide-column store partitioned by `user_id` and clustered by `timestamp`."

**5. Handling Edge Cases:**
**Say:** "To handle connection storms—like if a load balancer drops 1 million users at once—I will implement exponential backoff and jitter on the mobile clients. To prevent a celebrity user with 10,000 friends from crashing their localized Pub/Sub node, we can implement a threshold; if a user has $>1,000$ online friends, we switch them from a 'push' model to a 'pull' model, requiring clients to poll for that specific user's location."