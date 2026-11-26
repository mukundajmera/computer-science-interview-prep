# Interview Questions: DNS

## Core questions

### 1) Why does DNS matter in system design interviews?
DNS determines how clients discover endpoints. It directly affects latency, failover speed, and incident blast radius.

### 2) How does TTL affect reliability and performance?
Low TTL improves cutover speed but increases resolver/query load. High TTL improves caching but delays failover.

### 3) Can DNS alone replace load balancers?
No. DNS helps route clients to regions/endpoints, but per-request balancing, retries, and L7 policies still need load-balancing infrastructure.

### 4) What is the practical risk during record migration?
Split traffic due to cached old records; clients can continue hitting old endpoints until TTL expiry.

### 5) How do you do safer DNS cutover?
Lower TTL ahead of migration, validate new target under partial traffic, then switch records and monitor error/latency.

## Scenario questions

### 6) Your primary region is down. What does DNS failover not solve?
In-flight sessions and state consistency are not solved by DNS alone; application/state-layer failover must be designed.

### 7) Users in one geography report high latency. What DNS checks come first?
Verify geo/latency policy behavior, resolver path, edge PoP coverage, and whether stale cache pins users to distant endpoints.

### 8) Why can failover remain slow even with health checks?
Resolver and OS/client-side caches can hold stale records beyond expected control-plane change timing.

### 9) When do you use CNAME vs A/AAAA at the edge?
Use CNAME for aliasing managed endpoints; use A/AAAA for apex/root records where alias support is provider-dependent.

### 10) What metrics validate DNS strategy quality?
Resolution latency, NXDOMAIN/SERVFAIL rate, regional error rate post-change, and failover convergence time.

---

## Requirements and constraints

- Each answer should mention TTL and propagation behavior.
- Critical-path answers should include failover and rollback mechanics.
- Answers must distinguish control-plane routing from data-plane balancing.
- Include at least one monitoring signal tied to DNS behavior.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|-----------|---------------|-------------|
| Propagation awareness | Explains cached-state implications | Assumes instant update |
| Routing clarity | Differentiates DNS vs LB responsibilities | Collapses both into one layer |
| Reliability thinking | Includes failover caveats and rollback | No failure-mode awareness |
| Observability | Names concrete DNS health metrics | No measurable validation |

## Common pitfalls

- Ignoring local/recursive resolver cache behavior.
- Treating DNS failover as sufficient for stateful workloads.
- Forgetting pre-cutover TTL reduction.
- Overlooking DNS provider outage risk.

## Follow-up questions

- How would you design multi-provider DNS redundancy?
- What should be tested in a DNS game day?
- How do you explain DNS-caused partial outages to interviewers?

## Variants and extensions

- Active-active regional routing with weighted policies.
- Split-horizon DNS for internal service endpoints.
- Canary cutovers via weighted record adjustments.

## Related concepts

- [DNS Theory](./THEORY.md)
- [Load Balancing](../load-balancing/)
- [Service Discovery](../service-discovery/)
- [Networking Essentials](../../00-theory/networking-basics/networking-essentials.md)
- [Ride Sharing HLD](../../04-hld-projects/ride-sharing/)
