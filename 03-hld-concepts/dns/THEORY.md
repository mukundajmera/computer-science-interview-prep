# DNS

DNS maps human-readable names to network endpoints. In system design interviews, DNS is a control-plane dependency that affects availability, latency, and failover behavior.

## What DNS solves

- Abstracts changing infrastructure behind stable names.
- Enables global traffic steering (geo and latency-aware routing).
- Supports resilience with health-aware failover records.

## Core record types to know

- `A`/`AAAA`: name -> IPv4/IPv6 address.
- `CNAME`: alias name -> canonical name.
- `NS`: authoritative nameserver delegation.
- `TXT`: metadata (verification, policy records).

## Interview-relevant routing patterns

1. Weighted routing for gradual traffic shifts.
2. Latency/geo routing for global user proximity.
3. Failover routing tied to health checks.

## TTL strategy

- Lower TTL: faster failover and cutover, higher resolver load.
- Higher TTL: better cache hit ratio, slower propagation.
- Common practical pattern: lower TTL before migration; raise after stabilization.

## Operational failure points

- Resolver cache staleness after endpoint changes.
- Negative caching impact for transient NXDOMAIN mistakes.
- Control-plane outages at DNS provider or delegated zone misconfiguration.

---

## Requirements and constraints

- Define DNS ownership boundaries and change workflow.
- Set TTL by endpoint volatility and failover target.
- Ensure health-check and failover policy is explicit for critical services.
- Document disaster fallback if authoritative DNS provider is degraded.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|-----------|---------------|-------------|
| DNS role clarity | Treats DNS as control-plane dependency with latency/failover impact | Mentions DNS only as lookup step |
| TTL judgment | Balances propagation speed vs cache load | Arbitrary TTL values |
| Resilience | Explains health-based failover and rollback path | No outage plan |
| Practicality | Connects DNS strategy to product traffic patterns | Generic theory only |

## Common pitfalls

- Assuming DNS changes propagate instantly.
- Using one TTL policy for all records.
- Ignoring resolver and negative-cache behavior.
- Treating DNS as a data-plane load balancer replacement.

## Follow-up questions

- How would you perform zero-downtime regional migration with DNS?
- When do you choose DNS-based traffic steering vs L7 load balancing?
- How do you test DNS failover safely in production?

## Variants and extensions

- Anycast DNS provider setup for lower resolver latency.
- Split-horizon DNS for internal vs external clients.
- Multi-provider DNS for control-plane resilience.

## 📊 Diagrams

- [Recursive resolution with caching](./diagrams/recursive-resolution-caching.mmd) - the full lookup path from client to recursive resolver, root, TLD, and authoritative nameserver, with the resolver's cache short-circuiting the walk when a fresh answer is already stored.

## Related concepts

- [Networking Essentials](../../00-theory/networking-basics/networking-essentials.md)
- [Load Balancing](../load-balancing/)
- [CDN](../cdn/)
- [Service Discovery](../service-discovery/)
- [Video Streaming HLD](../../04-hld-projects/video-streaming/)
