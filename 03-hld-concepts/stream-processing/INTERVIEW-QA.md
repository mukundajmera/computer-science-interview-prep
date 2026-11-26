# Interview Questions: Stream Processing (Flink)

## Basic Questions

### 1. What is stream processing and why use Flink?

**A**: Stream processing handles continuous data flows in real-time, as opposed to batch processing which processes data in large chunks periodically.

**Flink advantages:**
- **True streaming**: Not micro-batching (vs Spark Streaming)
- **Event-time processing**: Handle out-of-order events correctly
- **Exactly-once semantics**: State consistency across failures
- **Low latency**: Millisecond to second range
- **Unified API**: Same code for batch and streaming

**Use cases:**
- Real-time analytics dashboards
- Fraud detection (financial transactions)
- IoT sensor data aggregation
- Live recommendations

---

### 2. Event time vs Processing time?

**A**:
- **Event time**: When event actually occurred
- **Processing time**: When system processes event

**Example**:
```
Mobile app generates click (event time: 10:00:00)
Network delay...
Server receives click (processing time: 10:00:05)

Event-time processing: Uses 10:00:00 (correct for analytics)
Processing-time processing: Uses 10:00:05 (incorrect results)
```

**When to use:**
- Event time: Historical replay, out-of-order handling
- Processing time: Simple cases, low latency critical

---

### 3. What are watermarks?

**A**: Watermarks signal progress in event time, indicating "all events up to time T have arrived."

```
Stream: Event(t=1) → Event(t=3) → Event(t=2) → Watermark(4)
                                    ↑ Out of order

Watermark(4) means: "All events with timestamp ≤ 4 have arrived"
→ Triggers window [0-5) computation
```

**Late data**: Events arriving after watermark can be handled with:
- Allowed lateness (grace period)
- Side outputs (separate stream)

---

### 4. Explain windowing in Flink

**A**:
**Tumbling windows** (non-overlapping):
```
[0-5) [5-10) [10-15)
Count events per 5-second window
```

**Sliding windows** (overlapping):
```
[0-10) [5-15) [10-20)
10-second window, 5-second slide
```

**Session windows** (gap-based):
```
Events: E1 E2 ─── E3 E4 ── E5
        [Session 1] [Session 2]
Gap = 2 seconds
```

**Use cases:**
- Tumbling: Periodic aggregates (every 5 minutes)
- Sliding: Moving averages
- Session: User activity sessions

---

### 5. How does Flink guarantee exactly-once?

**A**: **Asynchronous Barrier Snapshotting (Chandy-Lamport algorithm)**

```
1. JobManager injects checkpoint barrier into stream
2. Operators snapshot state when barrier passes
3. State saved to distributed storage (HDFS/S3)
4. All operators acknowledge → checkpoint complete

On failure:
- Restore from last checkpoint
- Replay from source (e.g., Kafka offset)
- Continue processing
```

**Exactly-once requires:**
- Replayable source (Kafka, file system)
- Idempotent or transactional sinks
- Checkpointing enabled

---

## Intermediate Questions

### 1. How would you implement real-time fraud detection?

**A**:
```java
// Detect: 3+ transactions in different countries within 10 minutes

Pattern<Transaction, ?> fraudPattern = Pattern
    .<Transaction>begin("first")
    .next("second")
    .where(new IterativeCondition<Transaction>() {
        @Override
        public boolean filter(Transaction tx, Context<Transaction> ctx) {
            Transaction first = ctx.getEventsForPattern("first").iterator().next();
            return !tx.country.equals(first.country);
        }
    })
    .next("third")
    .where(new IterativeCondition<Transaction>() {
        @Override
        public boolean filter(Transaction tx, Context<Transaction> ctx) {
            for (Transaction prev : ctx.getEventsForPattern("second")) {
                if (!tx.country.equals(prev.country)) return true;
            }
            return false;
        }
    })
    .within(Time.minutes(10));

DataStream<Transaction> transactions = ...;

PatternStream<Transaction> patternStream = CEP.pattern(
    transactions.keyBy(tx -> tx.userId),
    fraudPattern
);

DataStream<Alert> alerts = patternStream.select(
    (PatternSelectFunction<Transaction, Alert>) pattern -> {
        List<Transaction> all = new ArrayList<>();
        all.addAll(pattern.get("first"));
        all.addAll(pattern.get("second"));
        all.addAll(pattern.get("third"));
        return new Alert(all.get(0).userId, "Suspicious activity", all);
    }
);
```

---

### 2. What's the difference between stateless and stateful operations?

**A**:
**Stateless** (no memory):
```java
stream.map(x -> x * 2)  // Each event independent
```

**Stateful** (maintains state):
```java
// Running sum
stream
    .keyBy(x -> x.key)
    .sum("value")  // Remembers sum per key
```

**State types:**
- **ValueState**: Single value per key
- **ListState**: List of values
- **MapState**: Map per key
- **ReducingState**: Aggregated value

**Example with ValueState**:
```java
public class DeduplicationFunction extends KeyedProcessFunction<String, Event, Event> {
    private ValueState<Boolean> seenState;

    @Override
    public void open(Configuration config) {
        seenState = getRuntimeContext().getState(
            new ValueStateDescriptor<>("seen", Boolean.class, false)
        );
    }

    @Override
    public void processElement(Event event, Context ctx, Collector<Event> out) {
        if (!seenState.value()) {
            seenState.update(true);
            out.collect(event);  // First occurrence
        }
        // Subsequent occurrences ignored
    }
}
```

---

### 3. How would you handle late events?

**A**:
**1. Allowed lateness**:
```java
stream
    .keyBy(...)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .allowedLateness(Time.minutes(2))  // Grace period
    .sum("value");

// Window [0-5) closes at watermark 5, but accepts events until watermark 7
```

**2. Side outputs**:
```java
OutputTag<Event> lateTag = new OutputTag<Event>("late-events"){};

SingleOutputStreamOperator<Result> result = stream
    .keyBy(...)
    .window(...)
    .sideOutputLateData(lateTag)
    .sum("value");

DataStream<Event> lateEvents = result.getSideOutput(lateTag);
lateEvents.addSink(...);  // Handle separately
```

**3. Update results**:
```java
// Allow window updates for late data
stream
    .keyBy(...)
    .window(...)
    .allowedLateness(Time.hours(1))
    .aggregate(new AggregateFunction() {...})
    .addSink(new UpsertingSink());  // Updates previous results
```

---

## Advanced Questions

### 1. How would you design a real-time recommendation system?

**A**:
```java
// User behavior → Real-time model scoring → Recommendations

// Stream 1: User events
DataStream<UserEvent> userEvents = env.addSource(new KafkaSource<>(...));

// Stream 2: Item features (broadcast)
BroadcastStream<ItemFeature> itemFeatures = env
    .addSource(new ItemFeatureSource())
    .broadcast(new MapStateDescriptor<>("items", String.class, ItemFeature.class));

// Join and score
DataStream<Recommendation> recommendations = userEvents
    .keyBy(event -> event.userId)
    .connect(itemFeatures)
    .process(new RecommendationFunction());

class RecommendationFunction extends KeyedBroadcastProcessFunction<...> {
    private ValueState<UserProfile> profileState;
    private MapStateDescriptor<String, ItemFeature> itemsDescriptor;

    @Override
    public void processElement(UserEvent event, ReadOnlyContext ctx, Collector<Recommendation> out) {
        // Get user profile from state
        UserProfile profile = profileState.value();
        profile.update(event);
        profileState.update(profile);

        // Read item features from broadcast state
        ReadOnlyBroadcastState<String, ItemFeature> items =
            ctx.getBroadcastState(itemsDescriptor);

        // Score items
        List<ScoredItem> scored = new ArrayList<>();
        for (Map.Entry<String, ItemFeature> entry : items.immutableEntries()) {
            double score = computeScore(profile, entry.getValue());
            scored.add(new ScoredItem(entry.getKey(), score));
        }

        // Top K recommendations
        scored.sort(Comparator.comparingDouble(ScoredItem::getScore).reversed());
        out.collect(new Recommendation(event.userId, scored.subList(0, 10)));
    }

    @Override
    public void processBroadcastElement(ItemFeature item, Context ctx, Collector<Recommendation> out) {
        // Update broadcast state with new item features
        ctx.getBroadcastState(itemsDescriptor).put(item.itemId, item);
    }
}
```

---

### 2. How do you tune Flink performance?

**A**:
**Parallelism**:
```java
env.setParallelism(16);  // Cluster-wide default

stream
    .map(...)  // Uses default parallelism
    .setParallelism(32);  // Override for this operator
```

**Checkpointing**:
```java
env.enableCheckpointing(10000);  // Every 10 seconds
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(5000);  // Min 5s gap
env.getCheckpointConfig().setCheckpointTimeout(60000);  // 1-minute timeout
```

**Backpressure handling**:
- Monitor backpressure in Flink UI
- Increase parallelism of slow operators
- Use async I/O for external calls
- Tune buffer sizes

**Memory tuning**:
```yaml
taskmanager.memory.flink.size: 4gb
taskmanager.memory.task.heap.size: 2gb
taskmanager.memory.managed.size: 2gb
```

---

## Common Follow-ups

- "Flink vs Spark Streaming?"
- "How do you test Flink jobs?"
- "What happens during TaskManager failure?"
- "How do you monitor Flink applications?"

---

## Red Flags to Avoid

❌ **Don't say:**
- "Flink is micro-batching" - It's true streaming
- "Use processing time for everything" - Event time usually correct choice
- "Stateless is always better" - Many use cases need state

---

## How to Explain in 30 Seconds

> "Flink is a true stream processing framework with event-time semantics, exactly-once guarantees, and stateful computations. Key concepts: event time handles out-of-order data, watermarks trigger window computations, checkpointing provides fault tolerance. Use for real-time analytics, fraud detection, and CEP. Choose tumbling windows for periodic aggregates, session windows for user activity. Tune parallelism and checkpoint intervals for performance."
