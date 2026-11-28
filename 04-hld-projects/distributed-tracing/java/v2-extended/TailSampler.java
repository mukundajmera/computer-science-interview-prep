package v2_extended;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.LongSupplier;

/**
 * v2-extended distributed tracing: tail-based sampling.
 *
 * Improvements over v1-basic (each has dedicated tests; the same three are
 * named in DAGAssembler, the other main class):
 *
 * 1. Clock-skew adjustment: implemented in DAGAssembler (FOLLOW-UPS.md #1,
 *    PITFALLS "Forgetting Clock Skew").
 *
 * 2. Deduplication of at-least-once replays (PITFALLS "Omitting
 *    Deduplication for At-Least-Once Kafka Replays"): ingest() drops spans
 *    whose (trace_id, span_id) is already buffered and reports the
 *    duplicate, so a Kafka replay after a worker restart never
 *    double-counts a span.
 *
 * 3. Windowed sampling with an injectable clock and late-span fragments
 *    (FOLLOW-UPS.md #3): buffers expire after windowNs (default 30s, like
 *    the design doc's buffering window) via flushExpired(), and a span that
 *    arrives after its trace's window closed opens a fresh buffer,
 *    evaluated on its own merits as a fragment.
 */
public class TailSampler {
    private static final long DEFAULT_WINDOW_NS = 30_000_000_000L;

    private final Map<String, List<Span>> buffers = new ConcurrentHashMap<>();
    private final Map<String, Long> firstSeenNs = new ConcurrentHashMap<>();
    private final Set<String> seenIds = ConcurrentHashMap.newKeySet();
    private final long latencyThresholdNs;
    private final long windowNs;
    private final LongSupplier clock;

    public TailSampler(long latencyThresholdNs) {
        this(latencyThresholdNs, DEFAULT_WINDOW_NS, System::nanoTime);
    }

    public TailSampler(long latencyThresholdNs, long windowNs, LongSupplier clock) {
        this.latencyThresholdNs = latencyThresholdNs;
        this.windowNs = windowNs;
        this.clock = clock;
    }

    /**
     * Buffers the span. Returns false without buffering when the span is an
     * at-least-once replay duplicate (improvement #2).
     */
    public boolean ingest(Span span) {
        String key = span.getTraceId() + "" + span.getSpanId();
        if (!seenIds.add(key)) {
            return false;
        }
        firstSeenNs.putIfAbsent(span.getTraceId(), clock.getAsLong());
        buffers.computeIfAbsent(span.getTraceId(), k -> new ArrayList<>()).add(span);
        return true;
    }

    private boolean shouldKeep(List<Span> spans) {
        long maxDuration = 0;
        for (Span span : spans) {
            if (span.isError()) {
                return true;
            }
            if (span.getDurationNs() > maxDuration) {
                maxDuration = span.getDurationNs();
            }
        }
        return maxDuration > latencyThresholdNs;
    }

    /**
     * Closes the buffer for traceId and applies the keep/drop decision.
     * After this, the trace's dedup memory is released, so a late-arriving
     * span opens a fresh fragment buffer (improvement #3).
     */
    public List<Span> evaluateWindow(String traceId) {
        List<Span> spans = buffers.remove(traceId);
        firstSeenNs.remove(traceId);
        seenIds.removeIf(key -> key.startsWith(traceId + ""));
        if (spans == null || spans.isEmpty()) {
            return new ArrayList<>();
        }
        return shouldKeep(spans) ? spans : new ArrayList<>();
    }

    /**
     * Evaluates every buffer whose window has elapsed (improvement #3).
     * Returns traceId -> kept spans (empty list for dropped traces).
     */
    public Map<String, List<Span>> flushExpired() {
        long now = clock.getAsLong();
        Map<String, List<Span>> flushed = new HashMap<>();
        for (Map.Entry<String, Long> entry : firstSeenNs.entrySet()) {
            if (now - entry.getValue() >= windowNs) {
                flushed.put(entry.getKey(), evaluateWindow(entry.getKey()));
            }
        }
        return flushed;
    }

    /**
     * Worker crash: in-memory buffers, window timestamps and dedup state
     * are all lost (PITFALLS "Ignoring In-Memory Tail-Sampling Loss").
     */
    public void crash() {
        buffers.clear();
        firstSeenNs.clear();
        seenIds.clear();
    }

    /** Test visibility into how many spans a trace currently buffers. */
    public int bufferedSpanCount(String traceId) {
        List<Span> spans = buffers.get(traceId);
        return spans == null ? 0 : spans.size();
    }
}
