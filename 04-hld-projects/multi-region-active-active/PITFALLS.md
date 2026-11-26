# Common Pitfalls

- **Ignoring physical clock drift:** Relying solely on standard physical timestamps (NTP) for LWW will lead to silent data corruption when regional clocks drift by even a few milliseconds. For example, clock skew can cause a chronologically newer local write to be silently discarded because an older, delayed remote write arrived with an incorrectly advanced physical clock.
- **Synchronous replication over WAN:** Attempting two-phase commit (2PC) or synchronous replication across oceans will utterly fail the latency requirements (speed of light constraints). Cross-ocean WAN RTT will unavoidably break the strict p99 write latency requirements.
- **DNS caching during failover:** Assuming a simple DNS update will instantly shift traffic during a regional outage. Client and ISP DNS caches will cause significant downtime.
- **Unbounded replication queues:** Failing to account for storage limits on replication queues during a prolonged network partition. For example, an extended split-brain scenario could cause CDC queues to exhaust local disk space, resulting in crashed brokers and total node failure.
