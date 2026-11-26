# Follow-up Questions

1. **How do you handle clock skew between different servers when visualizing a trace?**
   *Rely on causal relationships (parent start/end time vs child start/end time) and adjust the child's timeline relative to the parent if it falls outside the parent's boundaries.*

2. **How does tail-based sampling work if spans for the same trace arrive at different worker nodes?**
   *You must partition the Kafka topics by `trace_id`. This ensures all spans belonging to the same trace go to the exact same consumer worker, allowing it to maintain the buffer locally.*

3. **What happens if a trace takes longer than the 30s buffering window in the tail sampler?**
   *It results in a fragmented trace. A late-arriving span will trigger a new buffer window. It might be dropped if it doesn't meet the sampling criteria on its own, leaving an incomplete trace in storage.*
