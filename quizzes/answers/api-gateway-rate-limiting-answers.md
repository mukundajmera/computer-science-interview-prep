# API Gateway and Rate Limiting Quiz - Answer Key

> **Detailed explanations for all 22 questions**

---

## Section 1: Core Concepts

### Question 1
**Answer: D) Token Bucket**

The Token Bucket algorithm adds tokens to a bucket at a fixed rate. If the bucket is full, new tokens are discarded. If a user makes a request, a token is removed. This allows users to save up tokens (up to the bucket capacity) and spend them all at once in a burst.

*Why others are wrong:*
- A: Leaky Bucket enforces a strict, constant outbound rate, smoothing out bursts.
- B: Fixed Window allows bursts, but suffers from the 'edge case' problem where double the limit can pass through around the window boundary.
- C: Strict queueing just delays traffic linearly.
---

### Question 2
**Answer: C) Leaky Bucket processes requests at a constant, steady rate, effectively smoothing out bursty traffic.**

In a Leaky Bucket, requests are added to a queue (the bucket). The queue is processed at a fixed, constant rate (the leak). If the queue is full, new requests are dropped. This strictly shapes traffic into a steady stream, unlike Token Bucket which allows sudden bursts.

*Why others are wrong:*
- A: Neither relies on a time window concept like Sliding Window does.
- B: This is exactly backwards.
- D: Both can be used for ingress or egress.
---

### Question 3
**Answer: D) It allows a spike of traffic up to twice the configured limit if requests are clustered precisely around the window boundary.**

If the limit is 100 requests per minute, a user could send 100 requests at 1:00:59, and another 100 requests at 1:01:01. The server processes 200 requests in a 2-second window, defeating the intended limit.

*Why others are wrong:*
- A: It only drops requests when the limit is exceeded.
- B: Fixed Window is actually the easiest to implement in Redis (using INCR).
- C: This describes Sliding Window Log.
---

### Question 4
**Answer: B) Sliding Window Log**

Sliding Window Log requires storing the timestamp of every request in a sorted set (like Redis ZSET) to accurately calculate the rolling window limit. For high-volume limits, this consumes significant memory.

*Why others are wrong:*
- A: Leaky Bucket just requires a queue length and a timer.
- C: Token Bucket just requires two integers: current tokens and last updated time.
- D: Fixed Window just requires one integer counter per window.
---

### Question 5
**Answer: B) It blends the current fixed window counter with a percentage of the previous fixed window counter based on the current time.**

Sliding Window Counter is a hybrid. If you are 30% into the current minute, it calculates your usage as `(current_minute_requests) + (previous_minute_requests * 0.7)`. This smooths the boundary spike while only requiring two integer counters in memory.

*Why others are wrong:*
- A: Timezones are irrelevant to rate limiting windows.
- C: Sampling violates strict rate limits.
- D: Encryption increases overhead and doesn't solve the algorithmic flaw.
---

### Question 6
**Answer: A) The circuit has detected failures and is immediately failing all incoming requests without attempting to contact the backend.**

An 'Open' circuit means the connection is broken. The circuit breaker intercepts calls and immediately returns an error (or fallback response) to prevent overwhelming a struggling backend.

*Why others are wrong:*
- B: This is the 'Half-Open' state.
- C: This is the 'Closed' state.
- D: This is normal router behavior, not a circuit breaker state.
---

### Question 7
**Answer: C) It allows a small, limited number of test requests to pass through to the backend to verify if it has recovered.**

After a timeout period in the Open state, the circuit transitions to Half-Open. It lets a few requests through. If they succeed, it assumes recovery and transitions to Closed. If they fail, it immediately reverts to Open.

*Why others are wrong:*
- A: It's a test probe, not a strict 50/50 load balancer.
- B: This is unrelated to resilience patterns.
- D: Circuit breakers are designed for automated recovery.
---

### Question 8
**Answer: B) Because counting the gateway's own rejections as backend failures creates an infinite loop where the circuit can never close.**

If the gateway rejects a request because the circuit is Open, that rejection is generated locally. If that rejection is counted against the backend's error rate, the error rate will remain artificially at 100%, and the circuit will never transition back to Half-Open or Closed.

*Why others are wrong:*
- A: 503 Service Unavailable is the standard code for this.
- C: The backend doesn't know about requests dropped at the gateway.
- D: While true, the logical deadlock (infinite loop) is the critical flaw.
---

### Question 9
**Answer: B) Partitioning resources (like thread pools or connection limits) so that a failure or slowdown in one downstream service doesn't consume all gateway resources and crash other services.**

Named after ship bulkheads, this pattern isolates failures. If Service A is slow, and the gateway uses a single global thread pool, all threads will eventually block waiting on Service A, bringing down Service B as well. Assigning separate, isolated thread/connection pools (bulkheads) per service prevents this.

*Why others are wrong:*
- A: This is a network topology concept.
- C: This is batching/multiplexing.
- D: This is a security mechanism.
---

### Question 10
**Answer: B) To sit in front of backend servers, accepting client requests, and forwarding them to the appropriate backend, abstracting the internal architecture.**

A reverse proxy sits 'reverse' to a standard forward proxy. Instead of protecting clients going out to the internet, it protects servers by accepting incoming internet traffic and securely distributing it to internal backend systems.

*Why others are wrong:*
- A: This describes a Web Application Firewall (WAF) or IDS, though NGINX can do some of this, it's not its primary definition.
- C: This describes a Forward Proxy (like a VPN or corporate proxy).
- D: Proxies are stateless routers, not databases.
---

### Question 11
**Answer: C) By using a Lua script (e.g., `EVAL`) executed within Redis.**

Fetching the current count and then incrementing it requires two network round trips and introduces a race condition if concurrent requests arrive. Redis executes Lua scripts atomically on the server side, ensuring the check-and-increment happens as a single indivisible operation.

*Why others are wrong:*
- A: System clocks are unreliable and don't solve atomicity.
- B: Eviction policies manage memory, not concurrency.
- D: Bloom filters check existence, not exact counts.
---

### Question 12
**Answer: A) X-Forwarded-For**

Because the backend receives the TCP connection from the API Gateway, the TCP source IP is the gateway's IP. To pass the actual client's IP, the gateway injects the `X-Forwarded-For` HTTP header.

*Why others are wrong:*
- B: Defines the payload format (e.g., JSON).
- C: Contains authentication credentials.
- D: Used to tell the client their quota status.
---

### Question 13
**Answer: C) The process of decrypting HTTPS traffic at the gateway layer, allowing the gateway to inspect the payload and forward unencrypted HTTP traffic to internal networks.**

By terminating SSL at the edge, the gateway offloads the CPU-intensive decryption work from the backend servers. It also allows the gateway to inspect the raw request (for routing, WAF, or rate limiting) before sending it via faster plaintext HTTP within the secure private VPC.

*Why others are wrong:*
- A: This is an IDS/WAF function.
- B: This is certificate revocation (CRL/OCSP).
- D: This is redundant and slows down performance.
---

### Question 14
**Answer: A) The IP address of the client.**

If a user isn't authenticated (no User ID or Token), the most reliable fallback identifier for rate limiting is their IP address, preventing a single machine from spamming anonymous endpoints (like login or signup).

*Why others are wrong:*
- B: User-Agents are easily spoofed and shared by millions of users.
- C: Email isn't known if they bypass login.
- D: MAC addresses do not traverse routers over the internet; the server only sees the gateway MAC.
---

### Question 15
**Answer: C) When a strict rate limit window resets (e.g., at the top of the hour), and thousands of blocked clients instantly retry at the exact same millisecond.**

If a strict Fixed Window algorithm blocks many users, they will all wait for the limit to reset. At the exact moment the window rolls over, all clients send their queued requests simultaneously, creating a massive spike that can overwhelm the backend.

*Why others are wrong:*
- A: This is an OOM error.
- B: Scaling helps handle load; it doesn't cause the herd.
- D: This is a fail-open scenario.
---

### Question 16
**Answer: D) Its ability to dynamically configure routing rules via xDS APIs without requiring a restart.**

Envoy's killer feature for modern cloud-native environments (like K8s) is its xDS APIs (Discovery Services). It can connect to a control plane and receive new routing rules, endpoints, and rate limits dynamically in memory without ever dropping connections or requiring a process reload.

*Why others are wrong:*
- A: Envoy is a proxy, not a database.
- B: Envoy is written in C++ and doesn't run Servlets.
- C: Envoy is completely independent of Apache.
---

### Question 17
**Answer: A) An API Gateway handles North-South traffic (internet to internal), while a Service Mesh (via sidecar proxies) handles East-West traffic (internal service to internal service).**

API Gateways sit at the edge (ingress), acting as the single entry point for external clients (North-South). A Service Mesh injects proxies (like Envoy) next to every single internal microservice to manage internal routing, mTLS, and observability between services (East-West).

*Why others are wrong:*
- B: They serve different architectural purposes.
- C: Both are typically software.
- D: Both can handle various protocols.
---

### Question 18
**Answer: A) Fail-Open allows all requests through, prioritizing availability; Fail-Closed blocks all requests, prioritizing protection.**

If the rate limiting dependency (Redis) goes offline, the system must choose a fallback. 'Fail-Open' assumes the traffic is valid and lets it pass to keep the business running (risking overload). 'Fail-Closed' assumes it's unsafe and blocks everything (causing 100% downtime but protecting the backend).

*Why others are wrong:*
- B: Neither involves modifying Redis data.
- C: While terms overlap with Circuit Breakers, in the context of dependency failure, it means allowing vs blocking traffic.
- D: Neither involves crashing the gateway process.
---

### Question 19
**Answer: D) To prevent the Thundering Herd problem where many clients simultaneously retry at exact exponential intervals.**

If multiple clients hit a rate limit and all retry exactly 2 seconds later (Exponential Backoff), they will crash into each other again. Adding a random 'jitter' (e.g., 2 seconds + random(0, 500ms)) spreads the retries out over time.

*Why others are wrong:*
- A: Load balancers determine backend routing, not client jitter.
- B: Jitter is a time concept, not encryption.
- C: It doesn't affect the API surface area.
---

### Question 20
**Answer: D) The client has exceeded their allocated rate limit and should slow down.**

HTTP 429 is the standard response code returned by a rate limiter when a client has exhausted their quota (e.g., Token Bucket is empty). It is usually accompanied by a `Retry-After` header telling the client how long to wait.

*Why others are wrong:*
- A: This would be a 404.
- B: This would be a 401.
- C: This would be a 500 or 503.
---

### Question 21
**Answer: A) Local rate limiting provides lower latency but allows traffic to exceed the global limit if requests are not evenly balanced across nodes.**

By keeping counters in memory on each gateway node, local rate limiting avoids the network latency of querying a centralized store like Redis. However, because nodes do not instantly share their counter states, a global limit of 100 req/sec might actually result in 300 req/sec passing through if traffic hits three independent gateway nodes simultaneously.

*Why others are wrong:*
- B: Local rate limiting is less accurate globally because it lacks synchronization between nodes.
- C: It requires less network bandwidth because it doesn't need to communicate with an external datastore on every request.
- D: Centralized datastores (if not clustered correctly) are more prone to being a single point of failure; local rate limiting makes nodes independent.

### Question 22
**Answer: D) Sliding Window Log; it guarantees precision but requires storing timestamps for every single request, leading to unbounded memory growth under heavy load.**

The Sliding Window Log algorithm precisely calculates limits by keeping an exact timestamp for each request in the rolling window. While it smoothly handles bursts without the edge-case doubling of Fixed Window, it suffers from severe memory bloat because an attacker generating massive traffic forces the gateway to store every timestamp, risking Out-Of-Memory (OOM) errors.

*Why others are wrong:*
- A: Token Bucket handles bursts well and is memory-efficient (just two counters: tokens and timestamp), though it does require atomicity, latency impact is minimal with Lua in Redis.
- B: Leaky Bucket shapes traffic into a steady stream and queues (delays) bursts rather than immediately dropping them, unless the queue itself is full.
- C: Fixed Window Counter is lightweight but suffers from the window boundary flaw (doubling the limit); it does not inherently require a single point of failure if distributed caches are clustered.



### Question 23
**Answer: B) Batching tokens in local memory avoids network hops to Redis on the critical path, significantly reducing latency at the cost of slight global precision.**

At high throughput (e.g., 100k QPS), hitting a centralized Redis instance on every request adds critical latency and risks overwhelming the store. By fetching a batch of tokens and caching them locally, the gateway can authorize most requests instantly in memory. The accepted trade-off is a slight loss of strict global precision (e.g., a node crash loses unused cached tokens, or momentary over-provisioning across nodes).

*Why others are wrong:*
- A: Redis can handle 100k+ QPS, but the network latency on the gateway's hot path is the primary concern for strict <10ms added latency constraints.
- C: An external datastore is still required to maintain the global state across distributed gateway nodes.
- D: The Lua script is still used, but only when fetching the next batch, not per-request.
