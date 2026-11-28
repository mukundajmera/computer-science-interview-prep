package v2_extended;

import java.util.ArrayList;
import java.util.List;

public class TraceDAGNode {
    private final Span span;
    private final List<TraceDAGNode> children;
    // Clock-skew adjusted timeline (v2 improvement #1), populated by
    // DAGAssembler.assemble; defaults to the raw span timeline.
    private long adjustedStartNs;
    private long adjustedEndNs;

    public TraceDAGNode(Span span) {
        this.span = span;
        this.children = new ArrayList<>();
        this.adjustedStartNs = span.getStartTimeNs();
        this.adjustedEndNs = span.getStartTimeNs() + span.getDurationNs();
    }

    public Span getSpan() { return span; }
    public List<TraceDAGNode> getChildren() { return children; }
    public void addChild(TraceDAGNode child) { children.add(child); }

    public long getAdjustedStartNs() { return adjustedStartNs; }
    public long getAdjustedEndNs() { return adjustedEndNs; }
    public void setAdjustedStartNs(long adjustedStartNs) { this.adjustedStartNs = adjustedStartNs; }
    public void setAdjustedEndNs(long adjustedEndNs) { this.adjustedEndNs = adjustedEndNs; }
}
