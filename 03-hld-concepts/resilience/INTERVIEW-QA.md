# Interview Questions: Resilience

Covers the folder's page on [cascading failure defense](cascading-failure-defense.md).

## Core Concepts

### 1. What is a cascading failure?
**Q**: Walk through how a small, localized slowdown becomes a full outage.
**A**: A cascading failure is a chain reaction: one component slows down, callers of that component see rising latency, and their connection and thread pools fill with in-flight requests waiting on the straggler. Those callers then time out, and their own callers start failing or retrying, so the load on the already-struggling component grows instead of shrinking. Layer by layer, healthy services are dragged down by resource exhaustion, not by any bug of their own. The [cascading failure page](cascading-failure-defense.md) frames the defense as defense-in-depth precisely because no single mechanism breaks every link of that chain.

### 2. Why do retries amplify an overload, and what makes a retry safe?
**Q**: Retries are supposed to improve reliability. How do they cause outages instead?
**A**: When a downstream service is overloaded, every timed-out request that gets retried is brand-new load on a system that already cannot keep up, so retries convert a capacity problem into a load multiplier. Safe retries need three properties: exponential backoff with jitter so retry storms do not synchronize, a retry budget that caps the fraction of traffic that may be retries, and deadlines so work is not retried after the caller has stopped caring. Without those, a retry policy is an accidental denial-of-service attack on your own dependencies. Follow-up: what is a retry storm and how does jitter defuse it?

### 3. What is graceful degradation, and what does it cost?
**Q**: Why return partial or stale results instead of an honest HTTP 500?
**A**: Graceful degradation keeps the system's primary purpose alive under stress by shedding quality rather than availability: serve cached or stale data, disable expensive features, or fall back to a simpler code path. Users get a slightly worse answer instead of no answer, which is usually the right business trade-off. The cost is correctness nuance: stale data can mislead, and a fallback path that nobody exercises in normal operation tends to be broken exactly when you need it. So degraded paths need the same testing and monitoring as primary paths. Follow-up: which features of a checkout flow would you degrade first, and which never?

### 4. What is load shedding, and where should it live?
**Q**: A service is past capacity. Why is deliberately dropping requests better than trying to serve them all?
**A**: Past capacity, attempting every request means the system thrashes and effectively serves none: queues grow, latencies explode past every timeout, and work is wasted on responses nobody waits for. Load shedding drops excess requests early and cheaply so the surviving requests get acceptable latency and the system stays alive to recover. It typically sits at the API gateway or reverse proxy, which can reject cheaply before work is invested, but it can also live inside the application when shedding needs application-level context. The trade-off is that shed requests are lost work, so you shed the least valuable traffic first, which is where priority queues come in.

### 5. How do priority drop queues change what gets shed?
**Q**: Under heavy load, how do you decide which requests to drop?
**A**: Priority drop queues classify incoming requests so shedding is selective rather than indiscriminate. In normal conditions everything is processed; under overload, low-priority traffic like background synchronization or analytics ingestion is dropped first while high-priority traffic like live user interactions or payment processing is preserved. This converts a blunt instrument into business-aware triage. The trade-offs are classification complexity and the risk of starving low-priority work during prolonged brownouts, so sustained shedding of a class should page someone rather than run silently forever.

### 6. What does Little's Law tell you about overload?
**Q**: How does `L = λ * W` explain connection pool exhaustion?
**A**: Little's Law says the concurrency inside a stable system equals the arrival rate times the average time each request spends inside: `L = λ * W`. When a dependency slows down, W (latency) rises while λ (arrival rate) stays constant, so L, the number of in-flight requests, grows automatically. Pools of threads and connections are finite, so rising L exhausts them, and once pools are exhausted the service cannot accept new work at all, even for healthy endpoints. This is the mathematical core of cascading failure: you cannot fix it by buying bigger pools, only by bounding concurrency or cutting latency. Follow-up: given 5,000 RPS and p50 latency rising from 50 ms to 2 s, what happens to required concurrency?

### 7. How do concurrency limiters defend a service, and how do you size them?
**Q**: Why cap in-flight requests instead of letting the queue absorb the burst?
**A**: A concurrency limiter caps the number of requests actively processed in parallel and sheds or briefly queues the rest, which keeps L bounded regardless of what latency does. The limit encodes the service's real capacity, so the system degrades by rejecting excess work instead of by collapsing. Sizing comes from measurement: find the concurrency where throughput saturates before latency degrades, and set the limit there, or use adaptive limiters that track latency and adjust automatically. A fixed limit set by guesswork is either too tight (wasted capacity) or too loose (no protection), which is why adaptive schemes exist.

### 8. What is bufferbloat, and how does CoDel fight it?
**Q**: Queues absorb bursts, so how can a queue make things worse?
**A**: A queue that is allowed to grow deep hides overload behind latency: every request waits so long in the buffer that it times out before being served, so the system burns capacity producing responses nobody wants. That is bufferbloat. CoDel (Controlled Delay) is an active queue management algorithm that watches the time requests spend in the queue; when the minimum sojourn time over a sliding window exceeds a target, it starts dropping, signaling senders to slow down through TCP congestion control or application-level backpressure. The [cascading failure page](cascading-failure-defense.md) applies the same idea to application-level queues: shed work whose queue time proves the downstream is falling behind, before stale requests consume the resources you need for recovery.

### 9. Design: your checkout service's inventory dependency is slowing down. What do you deploy, in what order?
**Q**: Assemble the defense-in-depth strategy for this scenario and justify the ordering.
**A**: First, put a concurrency limiter on calls to the inventory dependency so its latency cannot exhaust your pools (Little's Law), and add strict deadlines so no caller waits past its useful window. Second, make the failure graceful: fall back to cached inventory or defer the check with a clear user message instead of returning 500. Third, configure shedding at the gateway with priority classification so checkout traffic outranks background jobs if the whole service comes under pressure. Finally, fix retry policies everywhere in the chain (backoff, jitter, budgets) so your mitigations are not undone by retry storms. The ordering is containment first, then user experience, then traffic triage, then removal of amplifiers, because each layer buys time for the next one to matter.
