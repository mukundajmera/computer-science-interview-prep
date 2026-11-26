import v1_basic.Span;
import v1_basic.TailSampler;
import v1_basic.DAGAssembler;
import v1_basic.TraceDAGNode;

import java.util.Collections;
import java.util.List;

public class DistributedTracingTest {

    public static void main(String[] args) {
        testTailSampler_DropsNormalTrace();
        testTailSampler_KeepsErrorTrace();
        testTailSampler_KeepsSlowTrace();
        testDAGAssembler();
        testIngestionWorkerCrash_LosesInMemorySpans();
        System.out.println("All DistributedTracing Java tests passed.");
    }

    private static void testTailSampler_DropsNormalTrace() {
        TailSampler sampler = new TailSampler(1_000_000_000L); // 1s
        sampler.ingest(new Span("trace1", "span1", null, "svc1", "op1", 0, 500_000_000L, Collections.emptyMap(), false));
        
        List<Span> kept = sampler.evaluateWindow("trace1");
        if (!kept.isEmpty()) throw new AssertionError("Expected normal trace to be dropped");
    }

    private static void testTailSampler_KeepsErrorTrace() {
        TailSampler sampler = new TailSampler(1_000_000_000L);
        sampler.ingest(new Span("trace2", "span1", null, "svc1", "op1", 0, 500_000_000L, Collections.emptyMap(), false));
        sampler.ingest(new Span("trace2", "span2", "span1", "svc2", "op2", 0, 100_000_000L, Collections.emptyMap(), true)); // error
        
        List<Span> kept = sampler.evaluateWindow("trace2");
        if (kept.size() != 2) throw new AssertionError("Expected error trace to be kept");
    }

    private static void testTailSampler_KeepsSlowTrace() {
        TailSampler sampler = new TailSampler(1_000_000_000L);
        sampler.ingest(new Span("trace3", "span1", null, "svc1", "op1", 0, 1_500_000_000L, Collections.emptyMap(), false)); // >1s
        
        List<Span> kept = sampler.evaluateWindow("trace3");
        if (kept.size() != 1) throw new AssertionError("Expected slow trace to be kept");
    }
    
    private static void testDAGAssembler() {
        DAGAssembler assembler = new DAGAssembler();
        List<Span> spans = List.of(
            new Span("trace4", "root", null, "svc1", "op1", 0, 1000, Collections.emptyMap(), false),
            new Span("trace4", "child1", "root", "svc2", "op2", 100, 400, Collections.emptyMap(), false),
            new Span("trace4", "child2", "root", "svc3", "op3", 500, 300, Collections.emptyMap(), false)
        );
        
        List<TraceDAGNode> roots = assembler.assemble(spans);
        if (roots.size() != 1) throw new AssertionError("Expected 1 root");
        if (!roots.get(0).getSpan().getSpanId().equals("root")) throw new AssertionError("Root span ID mismatch");
        if (roots.get(0).getChildren().size() != 2) throw new AssertionError("Expected 2 children");
    }
    
    private static void testIngestionWorkerCrash_LosesInMemorySpans() {
        // Simplifications:
        // - Transport: Spans are passed as direct method calls, not over network (HTTP/gRPC)
        // - Clock: Durations are static provided values rather than computed from system time
        // - Security: Missing auth headers, tokens, and SSL encapsulation
        // - Consistency: Worker crash simulates local drop rather than partitioned Kafka replay issues
        TailSampler sampler = new TailSampler(1_000_000_000L);
        sampler.ingest(new Span("trace5", "span1", null, "svc1", "op1", 0, 1_500_000_000L, Collections.emptyMap(), false));
        sampler.crash();
        List<Span> kept = sampler.evaluateWindow("trace5");
        if (!kept.isEmpty()) throw new AssertionError("Expected buffers to be lost after crash");
    }
}
