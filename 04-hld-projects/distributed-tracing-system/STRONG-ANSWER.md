# Distributed Tracing System - Strong Answer

A highly successful interview response models a scalable tracing system that accurately handles Tail-Based sampling while accounting for the "Ingestion Worker Crash" failure invariant.

## System Narrative
"To handle 5 million spans per second, I'll design a decoupled ingestion pipeline. Applications will be instrumented with OpenTelemetry SDKs, propagating trace context via HTTP headers. Spans are sent asynchronously to a fleet of stateless Collectors. To prevent database overload during spikes, Collectors write all spans to a partitioned Kafka cluster.

Because we cannot afford to lose traces containing errors, we must use Tail-Based Sampling. Stream Processors will consume from Kafka, buffering spans in memory for 30 seconds to assemble the full trace DAG before making a sampling decision. Traces are stored using the CQRS pattern: raw spans go to Cassandra (keyed by Trace ID for high write throughput), while metadata goes to Elasticsearch to support complex user queries."

## Handling "Ingestion Worker Crash"
A critical failure invariant in Tail-Based sampling is the loss of in-memory state if a worker crashes before the 30-second window closes. In tracing, strict consistency is less important than availability. When a worker crashes, the spans buffered in memory are lost, but Kafka will re-deliver unacknowledged messages to a new worker. However, partial traces may have already been dropped. We accept this minor data loss as a trade-off for high throughput.

### Bounded Simulator

The following simulators model this invariant.

#### Python Implementation

```python
import time
import unittest
from typing import Dict, List, Optional

class Span:
    def __init__(self, trace_id: str, span_id: str, parent_id: Optional[str], duration: int, has_error: bool):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_id = parent_id
        self.duration = duration
        self.has_error = has_error

class TailSampler:
    def __init__(self, window_seconds: int = 30):
        self.buffer: Dict[str, List[Span]] = {}
        self.window_seconds = window_seconds
        
    def receive_span(self, span: Span):
        if span.trace_id not in self.buffer:
            self.buffer[span.trace_id] = []
        self.buffer[span.trace_id].append(span)
        
    def evaluate_trace(self, trace_id: str) -> bool:
        """Returns True if the trace should be sampled (kept), False if dropped."""
        if trace_id not in self.buffer:
            return False
            
        spans = self.buffer[trace_id]
        total_duration = sum(s.duration for s in spans)
        has_error = any(s.has_error for s in spans)
        
        # Sampling rules: Keep if error exists, or if very slow
        should_keep = has_error or total_duration > 2000
        
        # Clean up buffer after evaluation
        del self.buffer[trace_id]
        return should_keep

    def crash(self):
        """Simulates worker crash, losing all in-memory buffered spans."""
        self.buffer.clear()

class TestTracingWorkerCrash(unittest.TestCase):
    def test_worker_crash_loses_buffer(self):
        sampler = TailSampler()
        
        # Ingest spans for Trace A
        sampler.receive_span(Span("trace-A", "span-1", None, 500, False))
        sampler.receive_span(Span("trace-A", "span-2", "span-1", 100, True)) # Has error, should be kept
        
        # Simulate worker crash before the evaluation window closes
        sampler.crash()
        
        # Buffer is empty, trace evaluation is lost
        self.assertFalse(sampler.evaluate_trace("trace-A"))

if __name__ == '__main__':
    unittest.main()
```

#### Java Implementation

```java
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Span {
    String traceId;
    String spanId;
    String parentId;
    int duration;
    boolean hasError;

    public Span(String traceId, String spanId, String parentId, int duration, boolean hasError) {
        this.traceId = traceId;
        this.spanId = spanId;
        this.parentId = parentId;
        this.duration = duration;
        this.hasError = hasError;
    }
}

class TailSampler {
    private Map<String, List<Span>> buffer = new HashMap<>();
    
    public void receiveSpan(Span span) {
        buffer.computeIfAbsent(span.traceId, k -> new ArrayList<>()).add(span);
    }
    
    public boolean evaluateTrace(String traceId) {
        if (!buffer.containsKey(traceId)) {
            return false;
        }
        
        List<Span> spans = buffer.get(traceId);
        int totalDuration = 0;
        boolean hasError = false;
        
        for (Span s : spans) {
            totalDuration += s.duration;
            if (s.hasError) hasError = true;
        }
        
        boolean shouldKeep = hasError || totalDuration > 2000;
        
        buffer.remove(traceId);
        return shouldKeep;
    }
    
    // Models the invariant
    public void crash() {
        buffer.clear();
    }
}

public class TracingSimulatorTest {
    public static void main(String[] args) {
        testWorkerCrashLosesBuffer();
        System.out.println("Java TracingSimulatorTest passed.");
    }
    
    private static void testWorkerCrashLosesBuffer() {
        TailSampler sampler = new TailSampler();
        
        sampler.receiveSpan(new Span("trace-A", "span-1", null, 500, false));
        sampler.receiveSpan(new Span("trace-A", "span-2", "span-1", 100, true));
        
        sampler.crash();
        
        if (sampler.evaluateTrace("trace-A")) {
            throw new AssertionError("Expected trace to be dropped due to buffer loss");
        }
    }
}
```

### Simplifications Documented (CODE-WALKTHROUGH.md equivalent)
- **Transport:** The simulator omits the Kafka message queue and networking layer, invoking the sampler directly.
- **Clock / Time:** Real tail samplers use wall-clock or event-time timers to trigger the `evaluate_trace` function automatically when the window expires. Here, it is called manually.
- **Consistency:** The simulator assumes total loss of memory state upon crash and does not model Kafka's offset replay mechanisms, focusing solely on the vulnerability of the in-memory trace assembly buffer.
- **DAG Assembly:** The simulator calculates total duration as a simple sum, whereas a real system would assemble a DAG to find the critical path and handle parallel span executions.
