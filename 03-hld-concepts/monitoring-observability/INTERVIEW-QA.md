# Interview Questions: Monitoring & Observability

## Basic Questions

### 1. What are the three pillars of observability?
**Q**: Explain metrics, logs, and traces.

**A**:
- **Metrics**: Numeric time-series data (latency, error rate)
- **Logs**: Timestamped text records of events
- **Traces**: Request flow through distributed services

All three are needed for complete visibility.

---

### 2. What are SLIs, SLOs, and SLAs?
**Q**: Define these terms.

**A**:
- **SLI** (Service Level Indicator): What you measure (e.g., response time)
- **SLO** (Service Level Objective): Your target (e.g., p99 < 200ms)
- **SLA** (Service Level Agreement): External commitment with penalties

---

### 3. What are the four golden signals?
**Q**: What should you monitor for any service?

**A**:
1. **Latency**: How long requests take
2. **Traffic**: How many requests/second
3. **Errors**: What percentage fail
4. **Saturation**: How full is your system

---

## Intermediate Questions

### 4. How do you implement distributed tracing?
**Q**: How do you track a request across services?

**A**:
- Generate trace ID at entry point
- Pass trace ID in headers to all downstream services
- Each service logs its span (start/end times)
- Collect and visualize in tracing system (Jaeger)

---

### 5. What metrics would you track for a web service?
**Q**: Design metrics for an e-commerce API.

**A**:
- Request rate by endpoint
- Latency percentiles (p50, p95, p99)
- Error rate by type (4xx, 5xx)
- Database query time
- Cache hit rate
- Active connections

---

### 6. How do you prevent alert fatigue?
**Q**: Too many alerts, team ignores them. How to fix?

**A**:
- Alert on symptoms, not causes
- Set appropriate thresholds
- Use severity levels
- Implement alert suppression
- Regular review and pruning
- On-call runbooks

---

## Advanced Questions

### 7. What is coordinated omission in load testing?
**Q**: Why might a load test report a p99 latency of 5ms when users are experiencing 1-second stalls?

**A**:
This is likely **coordinated omission**, a flaw where the load tester uses a "closed-loop" (wait-for-response) model rather than an "open-loop" (fixed arrival rate) schedule.
- When the system stalls for 1 second, a closed-loop tester waits and fails to send the other requests that should have arrived during that second.
- It records only 1 slow request, rather than the 100 requests that would have queued up and experienced the stall in reality.
- This statistically erases the stall from the latency histogram, producing falsely optimistic p99 claims.

---

### 8. How do you calculate the end-to-end p99 of a distributed request?
**Q**: If Service A has a p99 of 100ms and calls Service B which has a p99 of 200ms, is the end-to-end p99 300ms?

**A**:
No, **percentiles are not additive**. The end-to-end p99 is usually much lower than 300ms.
- It is highly unlikely that the 1% worst-case request in Service A is the exact same request that hits the 1% worst-case latency in Service B.
- You cannot sum p99s, nor can you average them across shards. You must compute the global p99 from merged raw data or use specialized data structures (like T-Digest or HDRHistogram).

---

### 9. What is the fan-out tail effect?
**Q**: Why does a microservice architecture often suffer from high tail latency even if individual components are fast?

**A**:
Because of the **fan-out tail effect**.
- When a single user request scatters to multiple backend nodes (e.g., calling 10 services in parallel), the request is only as fast as the *slowest* response.
- If each service has a 1% chance of being slow, calling 10 services means there is a $1 - (0.99)^{10} \approx 9.5\%$ chance that the end-to-end request will be slow.
- The more services you call, the higher the probability of hitting a tail latency.

---

## How to Explain in 30 Seconds

"Observability has three pillars: metrics for numeric measurements over time, logs for detailed event records, and traces for tracking requests across services. You monitor the four golden signals—latency, traffic, errors, and saturation. Set SLOs based on user experience, and alert on symptoms not just causes. The key is correlating all three pillars with a common request ID to debug issues quickly."
