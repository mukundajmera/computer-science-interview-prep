import v2_extended.Span;
import v2_extended.TailSampler;
import v2_extended.DAGAssembler;
import v2_extended.TraceDAGNode;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;

public class DistributedTracingV2Test {

    private static final long NS = 1_000_000_000L;

    public static void main(String[] args) {
        // Parity with the v1 scenarios
        testTailSampler_DropsNormalTrace();
        testTailSampler_KeepsErrorTrace();
        testTailSampler_KeepsSlowTrace();
        testDAGAssembler();
        testIngestionWorkerCrash_LosesInMemorySpans();
        // Improvement #2: deduplication of at-least-once replays
        testIngestDeduplicatesReplays();
        testDedupAppliesInsideKeptTrace();
        testDagDeduplicatesDuplicateSpanIds();
        // Improvement #1: clock-skew adjustment
        testChildStartingBeforeParentIsClamped();
        testChildEndingAfterParentIsClamped();
        testWellFormedChildKeepsOriginalTimes();
        testSelfParentSpanTreatedAsRoot();
        // Improvement #3: windowed sampling with an injectable clock
        testFlushExpiredEvaluatesOldWindows();
        testFlushLeavesFreshWindowsBuffered();
        testLateSpanOpensNewFragmentWindow();
        System.out.println("All DistributedTracingV2 Java tests passed.");
    }

    // --- Parity ---

    private static void testTailSampler_DropsNormalTrace() {
        TailSampler sampler = new TailSampler(NS);
        sampler.ingest(new Span("trace1", "span1", null, "svc1", "op1", 0, 500_000_000L, Collections.emptyMap(), false));
        if (!sampler.evaluateWindow("trace1").isEmpty()) {
            throw new AssertionError("Expected normal trace to be dropped");
        }
    }

    private static void testTailSampler_KeepsErrorTrace() {
        TailSampler sampler = new TailSampler(NS);
        sampler.ingest(new Span("trace2", "span1", null, "svc1", "op1", 0, 500_000_000L, Collections.emptyMap(), false));
        sampler.ingest(new Span("trace2", "span2", "span1", "svc2", "op2", 0, 100_000_000L, Collections.emptyMap(), true));
        if (sampler.evaluateWindow("trace2").size() != 2) {
            throw new AssertionError("Expected error trace to be kept with both spans");
        }
    }

    private static void testTailSampler_KeepsSlowTrace() {
        TailSampler sampler = new TailSampler(NS);
        sampler.ingest(new Span("trace3", "span1", null, "svc1", "op1", 0, 1_500_000_000L, Collections.emptyMap(), false));
        if (sampler.evaluateWindow("trace3").size() != 1) {
            throw new AssertionError("Expected slow trace to be kept");
        }
    }

    private static void testDAGAssembler() {
        DAGAssembler assembler = new DAGAssembler();
        List<Span> spans = Arrays.asList(
                new Span("trace4", "root", null, "svc1", "op1", 0, 1000, Collections.emptyMap(), false),
                new Span("trace4", "child1", "root", "svc2", "op2", 100, 400, Collections.emptyMap(), false),
                new Span("trace4", "child2", "root", "svc3", "op3", 500, 300, Collections.emptyMap(), false));
        List<TraceDAGNode> roots = assembler.assemble(spans);
        if (roots.size() != 1 || !roots.get(0).getSpan().getSpanId().equals("root")
                || roots.get(0).getChildren().size() != 2) {
            throw new AssertionError("DAG assembly mismatch");
        }
    }

    private static void testIngestionWorkerCrash_LosesInMemorySpans() {
        TailSampler sampler = new TailSampler(NS);
        sampler.ingest(new Span("trace5", "span1", null, "svc1", "op1", 0, 1_500_000_000L, Collections.emptyMap(), false));
        sampler.crash();
        if (!sampler.evaluateWindow("trace5").isEmpty()) {
            throw new AssertionError("Expected crash to drop buffered spans");
        }
    }

    // --- Improvement #2: deduplication ---

    private static void testIngestDeduplicatesReplays() {
        TailSampler sampler = new TailSampler(NS);
        if (!sampler.ingest(new Span("t", "s1", null, "svc", "op", 0, 100, Collections.emptyMap(), false))) {
            throw new AssertionError("First ingest should be accepted");
        }
        if (sampler.ingest(new Span("t", "s1", null, "svc", "op", 0, 100, Collections.emptyMap(), false))) {
            throw new AssertionError("Replayed span should be rejected");
        }
        if (sampler.bufferedSpanCount("t") != 1) {
            throw new AssertionError("Expected exactly one buffered span");
        }
    }

    private static void testDedupAppliesInsideKeptTrace() {
        TailSampler sampler = new TailSampler(NS);
        sampler.ingest(new Span("t", "s1", null, "svc", "op", 0, 100, Collections.emptyMap(), true));
        sampler.ingest(new Span("t", "s1", null, "svc", "op", 0, 100, Collections.emptyMap(), true));
        if (sampler.evaluateWindow("t").size() != 1) {
            throw new AssertionError("Expected kept trace to contain one span, not the replay");
        }
    }

    private static void testDagDeduplicatesDuplicateSpanIds() {
        DAGAssembler assembler = new DAGAssembler();
        List<Span> spans = Arrays.asList(
                new Span("t", "root", null, "svc1", "op1", 0, 1000, Collections.emptyMap(), false),
                new Span("t", "child", "root", "svc2", "op2", 100, 400, Collections.emptyMap(), false),
                new Span("t", "child", "root", "svc2", "op2", 100, 400, Collections.emptyMap(), false));
        List<TraceDAGNode> roots = assembler.assemble(spans);
        if (roots.size() != 1 || roots.get(0).getChildren().size() != 1) {
            throw new AssertionError("Duplicate span_id should appear once in the DAG");
        }
    }

    // --- Improvement #1: clock-skew adjustment ---

    private static void testChildStartingBeforeParentIsClamped() {
        DAGAssembler assembler = new DAGAssembler();
        List<TraceDAGNode> roots = assembler.assemble(Arrays.asList(
                new Span("t", "root", null, "svc1", "op1", 1000, 1000, Collections.emptyMap(), false),
                new Span("t", "child", "root", "svc2", "op2", 500, 400, Collections.emptyMap(), false)));
        TraceDAGNode child = roots.get(0).getChildren().get(0);
        if (roots.get(0).getAdjustedStartNs() != 1000 || roots.get(0).getAdjustedEndNs() != 2000) {
            throw new AssertionError("Root timeline should be its raw span");
        }
        if (child.getAdjustedStartNs() != 1000 || child.getAdjustedEndNs() != 1000) {
            throw new AssertionError("Child starting before parent should be clamped to parent start");
        }
    }

    private static void testChildEndingAfterParentIsClamped() {
        DAGAssembler assembler = new DAGAssembler();
        List<TraceDAGNode> roots = assembler.assemble(Arrays.asList(
                new Span("t", "root", null, "svc1", "op1", 1000, 1000, Collections.emptyMap(), false),
                new Span("t", "child", "root", "svc2", "op2", 1200, 2000, Collections.emptyMap(), false)));
        TraceDAGNode child = roots.get(0).getChildren().get(0);
        if (child.getAdjustedStartNs() != 1200 || child.getAdjustedEndNs() != 2000) {
            throw new AssertionError("Child ending after parent should be clamped to parent end");
        }
    }

    private static void testWellFormedChildKeepsOriginalTimes() {
        DAGAssembler assembler = new DAGAssembler();
        List<TraceDAGNode> roots = assembler.assemble(Arrays.asList(
                new Span("t", "root", null, "svc1", "op1", 1000, 1000, Collections.emptyMap(), false),
                new Span("t", "child", "root", "svc2", "op2", 1100, 400, Collections.emptyMap(), false)));
        TraceDAGNode child = roots.get(0).getChildren().get(0);
        if (child.getAdjustedStartNs() != 1100 || child.getAdjustedEndNs() != 1500) {
            throw new AssertionError("Well-formed child timeline should be untouched");
        }
    }

    private static void testSelfParentSpanTreatedAsRoot() {
        DAGAssembler assembler = new DAGAssembler();
        List<TraceDAGNode> roots = assembler.assemble(Collections.singletonList(
                new Span("t", "loop", "loop", "svc1", "op1", 0, 100, Collections.emptyMap(), false)));
        if (roots.size() != 1 || !roots.get(0).getChildren().isEmpty()) {
            throw new AssertionError("Self-parent span should surface as a childless root");
        }
    }

    // --- Improvement #3: windowed sampling ---

    private static void testFlushExpiredEvaluatesOldWindows() {
        long[] now = {0};
        TailSampler sampler = new TailSampler(NS, 30 * NS, () -> now[0]);
        sampler.ingest(new Span("t", "s1", null, "svc", "op", 0, 100, Collections.emptyMap(), true));
        now[0] = 31 * NS;
        Map<String, List<Span>> flushed = sampler.flushExpired();
        if (flushed.size() != 1 || flushed.get("t").size() != 1) {
            throw new AssertionError("Expired error window should be flushed and kept");
        }
        if (!sampler.evaluateWindow("t").isEmpty()) {
            throw new AssertionError("Flushed window should already be closed");
        }
    }

    private static void testFlushLeavesFreshWindowsBuffered() {
        long[] now = {0};
        TailSampler sampler = new TailSampler(NS, 30 * NS, () -> now[0]);
        sampler.ingest(new Span("t", "s1", null, "svc", "op", 0, 100, Collections.emptyMap(), false));
        now[0] = 10 * NS;
        if (!sampler.flushExpired().isEmpty() || sampler.bufferedSpanCount("t") != 1) {
            throw new AssertionError("Fresh window should stay buffered");
        }
    }

    private static void testLateSpanOpensNewFragmentWindow() {
        long[] now = {0};
        TailSampler sampler = new TailSampler(NS, 30 * NS, () -> now[0]);
        sampler.ingest(new Span("t", "s1", null, "svc", "op", 0, 100, Collections.emptyMap(), false));
        if (!sampler.evaluateWindow("t").isEmpty()) {
            throw new AssertionError("Normal trace should be dropped");
        }
        if (!sampler.ingest(new Span("t", "s2", null, "svc", "op", 0, 2 * NS, Collections.emptyMap(), false))) {
            throw new AssertionError("Late span should open a fresh fragment buffer");
        }
        if (sampler.evaluateWindow("t").size() != 1) {
            throw new AssertionError("Slow fragment should be kept on its own merits");
        }
    }
}
