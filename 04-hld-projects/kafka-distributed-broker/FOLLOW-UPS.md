# Follow-up Questions

1. **How do you handle consumer group rebalancing?**
   - Use a Group Coordinator (a specific broker) that assigns partitions to consumers.
2. **What happens if a broker's disk fills up?**
   - Implement retention policies (size-based or time-based segment deletion) and monitor disk usage.
3. **How is Exactly-Once Semantics (EOS) achieved?**
   - By combining idempotent producers (using sequence numbers) and transactional writes across partitions.
4. **How do you optimize tail reads vs historical reads?**
   - Tail reads hit the page cache; historical reads require disk I/O, which should be isolated or throttled to avoid impacting tail latency.
