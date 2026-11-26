package v1_basic;

import java.util.ArrayList;
import java.util.List;

public class TraceDAGNode {
    private final Span span;
    private final List<TraceDAGNode> children;

    public TraceDAGNode(Span span) {
        this.span = span;
        this.children = new ArrayList<>();
    }

    public Span getSpan() { return span; }
    public List<TraceDAGNode> getChildren() { return children; }
    public void addChild(TraceDAGNode child) { children.add(child); }
}
