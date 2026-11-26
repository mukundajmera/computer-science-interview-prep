package v1_basic;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class TailSampler {
    private final Map<String, List<Span>> buffers = new ConcurrentHashMap<>();
    private final long latencyThresholdNs;
    
    public TailSampler(long latencyThresholdNs) {
        this.latencyThresholdNs = latencyThresholdNs;
    }

    public void ingest(Span span) {
        buffers.computeIfAbsent(span.getTraceId(), k -> new ArrayList<>()).add(span);
    }

    public List<Span> evaluateWindow(String traceId) {
        List<Span> spans = buffers.remove(traceId);
        if (spans == null || spans.isEmpty()) {
            return new ArrayList<>();
        }

        boolean keep = false;
        long maxDuration = 0;
        
        for (Span span : spans) {
            if (span.isError()) {
                keep = true;
                break;
            }
            if (span.getDurationNs() > maxDuration) {
                maxDuration = span.getDurationNs();
            }
        }
        
        if (!keep && maxDuration > latencyThresholdNs) {
            keep = true;
        }

        return keep ? spans : new ArrayList<>();
    }
    
    public void crash() {
        buffers.clear();
    }
}
