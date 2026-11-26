# Stream Processing (Apache Flink)

**Code and tests**: See [Flink](../flink/THEORY.md) for canonical code and tests.

## What is it?

Apache Flink is a distributed stream processing framework for stateful computations over unbounded (streaming) and bounded (batch) data streams. It provides true streaming with low latency, exactly-once semantics, and advanced event-time processing capabilities.

## Why do we need it?

**Problem it solves**: Real-time data processing at scale requires handling out-of-order events, managing state across distributed nodes, and providing fault tolerance—challenges that traditional batch processing and simple streaming cannot address efficiently.

**Without Stream Processing**:
- Batch processing has high latency (hours/days)
- Simple message consumers lose state on failure
- No handling of out-of-order or late events
- Difficult to implement complex event processing
- Manual windowing and aggregation logic

**With Flink**:
- Millisecond to second latency for stream processing
- Exactly-once state consistency across failures
- Event-time processing with watermarks for late data
- Built-in windowing, joins, and aggregations
- Horizontal scaling across machines

## Core Concepts

### 1. Streams vs Batch

```
Unbounded Stream (infinite):
Event 1 → Event 2 → Event 3 → Event 4 → Event 5 → ...
[No end, continuous processing]

Bounded Stream (finite):
Event 1 → Event 2 → Event 3 → Event 4 [END]
[Batch processing as special case of streaming]
```

**Flink treats batch as bounded stream**, enabling unified API.

### 2. Event Time vs Processing Time

```
Event Time: When event actually occurred
Processing Time: When event is processed by system

Scenario: Network delay
Event generated: 10:00:00 (event time)
Event arrives:   10:00:05 (processing time)

Event time processing handles:
- Out-of-order events
- Late arrivals
- Replaying historical data
```

### 3. Watermarks

Watermarks signal progress in event time:

```
Stream with timestamps:
Event 1 (t=1) → Event 2 (t=3) → Event 3 (t=2) → Event 4 (t=5)
                                    ↑ Out of order

Watermark(4) → "All events with t ≤ 4 have arrived"
               → Triggers window [0-5) computation
```

**Late data handling**:
```
Window [0-5) with watermark tolerance of 2 seconds
- Event (t=4) arrives → included in window
- Event (t=3) arrives late → still included (within tolerance)
- Event (t=1) arrives very late → discarded or sent to side output
```

### 4. Stateful Processing

Flink maintains state across events:

```
Stateless:
Event 1 → Process → Output 1
Event 2 → Process → Output 2
(No memory of Event 1)

Stateful:
Event 1 → Process → Update State → Output 1
Event 2 → Process → Read State → Update State → Output 2
(Remembers past events)
```

**Example: Running sum**
```java
// State: sum = 0
Event 1 (value=5)  → sum = 5  → output: 5
Event 2 (value=3)  → sum = 8  → output: 8
Event 3 (value=10) → sum = 18 → output: 18
```

## Architecture

```
Flink Cluster
├── JobManager (Master)
│   ├── Schedules tasks
│   ├── Coordinates checkpoints
│   └── Manages failure recovery
└── TaskManagers (Workers)
    ├── TaskManager 1
    │   ├── Task Slot 1 (Source → Map)
    │   └── Task Slot 2 (KeyBy → Window)
    ├── TaskManager 2
    │   ├── Task Slot 1 (Map → KeyBy)
    │   └── Task Slot 2 (Window → Sink)
    └── TaskManager 3
        └── Task Slot 1 (Sink)
```

**Task distribution**:
```
Application DAG:
Source → Map → KeyBy → Window → Aggregate → Sink
  ↓
Distributed across TaskManagers
  ↓
Parallelism = 4:
TM1: Source-1, Map-1
TM2: Source-2, Map-2
TM3: KeyBy-1, Window-1
TM4: KeyBy-2, Window-2
```

## How it works

### 1. Windowing

**Tumbling Windows** (non-overlapping):
```
Time: 0  1  2  3  4  5  6  7  8  9
      [Window 1][Window 2][Window 3]
      Events in each window processed separately
```

**Sliding Windows** (overlapping):
```
Time: 0  1  2  3  4  5  6  7  8
      [Window 1]
         [Window 2]
            [Window 3]
      Window size=3, slide=1
```

**Session Windows** (gap-based):
```
Events: E1 E2 ─── E3 E4 ── E5 ─────── E6 E7
        [Session 1] [Session 2] [Session 3]
        Gap timeout = 2 seconds
```

**Example code**:
```java
// Tumbling window: 5-minute intervals
stream
    .keyBy(event -> event.userId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .sum("value");

// Sliding window: 10-minute window, 5-minute slide
stream
    .keyBy(event -> event.userId)
    .window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(5)))
    .sum("value");

// Session window: 30-minute gap
stream
    .keyBy(event -> event.userId)
    .window(EventTimeSessionWindows.withGap(Time.minutes(30)))
    .aggregate(new SessionAggregator());
```

### 2. Stateful Operations

**Keyed State** (per key):
```java
public class RunningSumFunction extends KeyedProcessFunction<String, Event, Long> {
    private ValueState<Long> sumState;

    @Override
    public void open(Configuration config) {
        ValueStateDescriptor<Long> descriptor =
            new ValueStateDescriptor<>("sum", Long.class, 0L);
        sumState = getRuntimeContext().getState(descriptor);
    }

    @Override
    public void processElement(Event event, Context ctx, Collector<Long> out) {
        Long currentSum = sumState.value();
        Long newSum = currentSum + event.value;
        sumState.update(newSum);
        out.collect(newSum);
    }
}
```

**Operator State** (per parallel instance):
```java
// Example: Buffered sink with checkpoint
public class BufferedSink implements CheckpointedFunction {
    private List<Event> buffered = new ArrayList<>();
    private ListState<Event> checkpointedState;

    @Override
    public void snapshotState(FunctionSnapshotContext context) {
        checkpointedState.clear();
        checkpointedState.addAll(buffered);
    }

    @Override
    public void initializeState(FunctionInitializationContext context) {
        checkpointedState = context.getOperatorStateStore()
            .getListState(new ListStateDescriptor<>("buffered", Event.class));

        if (context.isRestored()) {
            buffered.addAll(checkpointedState.get());
        }
    }
}
```

### 3. Checkpointing (Fault Tolerance)

```
Normal Processing:
Source → Map → KeyBy → Window → Sink
  ↓
Periodic Checkpoint (e.g., every 10 seconds):
  ↓
Snapshot state to distributed storage (HDFS/S3):
- Source offset: 10000
- Map state: {...}
- Window state: {...}
  ↓
On Failure:
  ↓
Restore from last checkpoint:
- Source: Resume from offset 10000
- Operators: Restore state
  ↓
Continue processing (exactly-once guaranteed)
```

**Asynchronous Barrier Snapshotting**:
```
Checkpoint Barrier flows through stream:

Source [Checkpoint 5 barrier] → Event A → Event B → ...
   ↓
Map operator receives barrier:
   - Snapshot state
   - Forward barrier downstream
   ↓
Window operator receives barrier:
   - Snapshot state
   - Forward barrier downstream
   ↓
Sink operator receives barrier:
   - Snapshot state
   - Acknowledge checkpoint complete
```

## Use Cases

### 1. Real-Time Analytics

```java
// Example: Real-time page view statistics
DataStream<PageView> pageViews = ...;

pageViews
    .keyBy(view -> view.pageId)
    .window(TumblingEventTimeWindows.of(Time.minutes(5)))
    .aggregate(new PageViewAggregator())
    .addSink(new DashboardSink());

class PageViewAggregator implements AggregateFunction<PageView, PageStats, PageStats> {
    public PageStats createAccumulator() {
        return new PageStats(0, 0.0);
    }

    public PageStats add(PageView view, PageStats acc) {
        return new PageStats(
            acc.count + 1,
            acc.totalDuration + view.duration
        );
    }

    public PageStats getResult(PageStats acc) {
        acc.avgDuration = acc.totalDuration / acc.count;
        return acc;
    }

    public PageStats merge(PageStats a, PageStats b) {
        return new PageStats(
            a.count + b.count,
            a.totalDuration + b.totalDuration
        );
    }
}
```

### 2. Complex Event Processing

```java
// Pattern: Detect 3 failed login attempts within 5 minutes
Pattern<LoginEvent, ?> pattern = Pattern
    .<LoginEvent>begin("first")
    .where(evt -> evt.status.equals("failed"))
    .next("second")
    .where(evt -> evt.status.equals("failed"))
    .next("third")
    .where(evt -> evt.status.equals("failed"))
    .within(Time.minutes(5));

PatternStream<LoginEvent> patternStream =
    CEP.pattern(loginEvents.keyBy(evt -> evt.userId), pattern);

patternStream.select((PatternSelectFunction<LoginEvent, Alert>) pattern -> {
    LoginEvent first = pattern.get("first").get(0);
    return new Alert(first.userId, "3 failed logins detected");
});
```

### 3. Stream Joins

```java
// Join orders with shipments within 1-hour window
DataStream<Order> orders = ...;
DataStream<Shipment> shipments = ...;

orders.join(shipments)
    .where(order -> order.orderId)
    .equalTo(shipment -> shipment.orderId)
    .window(TumblingEventTimeWindows.of(Time.hours(1)))
    .apply((order, shipment) -> new OrderShipment(order, shipment));
```

## When to use

✅ **Use Flink when:**
- Real-time analytics with sub-second latency
- Complex event processing (CEP)
- Event-time processing with late data handling
- Stateful stream processing with exactly-once
- Stream joins and aggregations at scale
- Both streaming and batch in unified pipeline

**Specific scenarios:**
- Fraud detection systems
- Real-time recommendations
- IoT sensor data processing
- Financial trading systems
- Log aggregation and alerting
- Continuous ETL pipelines

## When NOT to use

❌ **Avoid or reconsider when:**
- Simple message queue processing (use Kafka consumers)
- Batch-only workloads (use Spark for simplicity)
- Very low throughput (<1000 events/sec)
- No state management needed
- Team unfamiliar with stream processing concepts

**Consider alternatives:**
- **Kafka Streams**: Simpler, library-based
- **Spark Streaming**: Better for batch + streaming hybrid
- **Storm**: Lower latency but less mature
- **Cloud-native**: AWS Kinesis, Google Dataflow

## Trade-offs

| Aspect | Benefit | Cost |
|--------|---------|------|
| **True streaming** | Low latency (milliseconds) | More complex than micro-batching |
| **Exactly-once** | Strong consistency | Checkpoint overhead |
| **Event-time** | Correct results for late data | Watermark tuning required |
| **Stateful** | Complex processing | State management overhead |
| **Unified API** | Same code for batch/stream | Steeper learning curve |

## Real-world examples

### Alibaba
- **Usage**: Real-time search ranking
- **Scale**: Trillions of events per day
- **Pattern**: Event-time processing with state

### Uber
- **Usage**: Real-time pricing, driver-rider matching
- **Pattern**: Geospatial stream processing

### Netflix
- **Usage**: Real-time operational monitoring
- **Pattern**: Complex event processing for anomaly detection

## Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| **Map** | O(1) | Per event |
| **Filter** | O(1) | Per event |
| **KeyBy** | O(1) | Partitioning by hash |
| **Window aggregate** | O(N) | N = events in window |
| **Join** | O(N + M) | N, M = events in each stream |

## Key Takeaways

1. **True streaming**: Not micro-batching; millisecond latency
2. **Event time > Processing time**: Handle out-of-order events
3. **Watermarks signal progress**: Trigger window computations
4. **Stateful processing**: Maintain state across events
5. **Exactly-once guarantees**: Checkpointing for fault tolerance
6. **Unified batch/stream**: Batch as bounded stream
7. **Complex event processing**: Pattern detection built-in

---

## Related Concepts
- [Message Queues](../message-queues/) - Kafka as input source
- [Time-Series Databases](../time-series-databases/) - Output destination
- [Distributed Coordination](../distributed-coordination/) - Cluster coordination

## Flink Overview

## Why do we need it?

Some systems require near-real-time aggregation, enrichment, and anomaly detection where batch latency is too slow. Flink is designed for these event-time and stateful stream workloads.

## Types/Approaches

### 1. Processing Model
- **Stateless transformations**: map/filter/enrich.
- **Stateful operators**: keyed counters, joins, session logic.

### 2. Time Semantics
- **Event time**: based on event timestamp, robust to delay/out-of-order data.
- **Processing time**: based on machine clock, simpler but less accurate.

### 3. Windowing
- **Tumbling**: fixed non-overlapping windows.
- **Sliding**: overlapping windows.
- **Session**: gap-based user/activity sessions.

## How it works

### Stream job architecture
1. Sources ingest events (Kafka, files, CDC, etc.).
2. Operators transform and aggregate events.
3. State backend stores keyed/window state.
4. Checkpoints provide recovery guarantees.
5. Sinks publish outputs (DB, Kafka, storage).

### Watermarks and correctness
- Watermarks approximate progress in event time.
- Late data policies decide drop, retraction, or update behavior.

### Reliability model
- Checkpointing + replay enables strong delivery guarantees.
- Exactly-once semantics require sink and source integration support.

## When to use

- Real-time metrics pipelines and alerting.
- Stateful stream aggregations with strict latency goals.
- Continuous joins across multiple event streams.

## When NOT to use

- Workloads where hourly/daily batch latency is acceptable.
- Tiny workloads where operational overhead outweighs benefit.
- Teams without operational readiness for stateful stream systems.

## Trade-offs

| Pros | Cons |
|------|------|
| Low-latency stateful stream processing | Higher operational complexity than batch |
| Strong event-time correctness support | Windowing/watermark tuning can be tricky |
| Robust checkpoint/recovery model | Stateful jobs need careful scaling and backfill design |
| Rich connectors and operators | Exactly-once end-to-end depends on sink/source support |

## Interview checklist

1. Confirm real-time latency requirement is real.
2. Choose event time vs processing time explicitly.
3. Define windows, watermark policy, and late-data behavior.
4. Explain state size, checkpoint cadence, and recovery.
5. Discuss backpressure and scaling strategy.

## Real-world examples

- Ad click aggregation and fraud counters.
- Real-time observability metrics pipeline.
- Transaction risk scoring in event streams.

## Key Takeaways

1. Flink is most valuable when correctness + low latency both matter.
2. Event-time thinking is central for reliable stream outputs.
3. Stateful streaming requires explicit recovery and backpressure plans.
4. Not every stream-like problem needs a stream processor.

