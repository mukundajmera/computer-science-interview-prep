package v2_extended;

import java.util.Map;
import java.util.Objects;

public class Span {
    private final String traceId;
    private final String spanId;
    private final String parentSpanId;
    private final String serviceName;
    private final String operationName;
    private final long startTimeNs;
    private final long durationNs;
    private final Map<String, String> tags;
    private boolean isError;

    public Span(String traceId, String spanId, String parentSpanId, String serviceName,
                String operationName, long startTimeNs, long durationNs, Map<String, String> tags, boolean isError) {
        this.traceId = traceId;
        this.spanId = spanId;
        this.parentSpanId = parentSpanId;
        this.serviceName = serviceName;
        this.operationName = operationName;
        this.startTimeNs = startTimeNs;
        this.durationNs = durationNs;
        this.tags = tags;
        this.isError = isError;
    }

    public String getTraceId() { return traceId; }
    public String getSpanId() { return spanId; }
    public String getParentSpanId() { return parentSpanId; }
    public String getServiceName() { return serviceName; }
    public String getOperationName() { return operationName; }
    public long getStartTimeNs() { return startTimeNs; }
    public long getDurationNs() { return durationNs; }
    public Map<String, String> getTags() { return tags; }
    public boolean isError() { return isError; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Span span = (Span) o;
        return Objects.equals(traceId, span.traceId) && Objects.equals(spanId, span.spanId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(traceId, spanId);
    }
}
