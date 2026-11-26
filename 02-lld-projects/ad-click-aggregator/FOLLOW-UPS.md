# Follow-Ups for Ad Click Aggregator

## Future Enhancements and Scalability Challenges
While the current custom-built stream processing architecture handles the immediate requirements for aggregating click events and managing basic windows, scaling the system to handle 10x traffic and supporting more complex analytical queries will require significant architectural evolution.

### 1. Migration to a Distributed Stream Processing Engine
The current **v3-optimized** implementation requires manual management of watermarks, window eviction, and state checkpointing.
- **Action Item:** Evaluate migrating the core aggregation logic to a dedicated distributed stream processing framework. 
- **Rationale:** These frameworks provide highly optimized, built-in mechanisms for exactly-once processing and robust failure recovery. As our single-node solutions (like **v1-basic** and **v2-extended**) show limits, a distributed model still enforces our core constraints: duplicate event IDs affect billing aggregates exactly once; probabilistic filters only accelerate an exact deduplication check. We also continue ensuring empty input and invalid event payloads fail predictably.
- **Trade-off:** Introducing a framework adds operational complexity compared to our standard-library implementations.

### 2. Implementing Approximate Counting for High Cardinality
As the business requirements evolve, product managers may request distinct counting metrics, such as "Unique Users per Ad Campaign" rather than just total clicks.
- **Action Item:** Integrate standard-library probabilistic data structures (e.g., custom HyperLogLog equivalents) into the aggregation state.
- **Rationale:** Storing exact sets of `user_id`s in memory for every active ad campaign to calculate uniqueness is fundamentally unscalable.
- **Trade-off:** We trade absolute precision for massive scalability in non-billing unique counts.

### 3. Advanced Windowing Policies
Ad traffic requires advanced window management to track user engagement.
- **Action Item:** Extend the basic windowing strategy to handle dynamic and session windows.
- **Rationale:** Expanding on how window-boundary, late-event and out-of-order timestamp examples state processing-time/event-time policy will allow us to accurately capture bursts of user interactions in real-time.
- **Trade-off:** Implementing session windows adds significant state tracking overhead compared to fixed tumbling windows.

### 4. Advanced Fraud Detection Integration
Basic deduplication handles retries, but it does not stop coordinated botnets generating fraudulent clicks to drain a competitor's advertising budget.
- **Action Item:** Implement an asynchronous machine learning pipeline. 
- **Rationale:** Raw events should be teed off to a separate system that analyzes patterns in real-time, looking for anomalies like impossible click velocities from specific IP subnets, suspicious user agents, or click farms. This system can generate probabilistic fraud scores.
- **Trade-off:** This adds significant complexity. We must decide whether to block suspicious clicks inline (increasing latency) or process them asynchronously and issue retro-active credits to the advertiser (increasing billing complexity). Asynchronous processing is generally preferred to maintain high throughput.
