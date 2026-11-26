package v1_basic;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class DAGAssembler {
    
    public List<TraceDAGNode> assemble(List<Span> spans) {
        Map<String, TraceDAGNode> nodeMap = new HashMap<>();
        List<TraceDAGNode> roots = new ArrayList<>();

        for (Span span : spans) {
            nodeMap.put(span.getSpanId(), new TraceDAGNode(span));
        }

        for (Span span : spans) {
            TraceDAGNode node = nodeMap.get(span.getSpanId());
            if (span.getParentSpanId() == null || span.getParentSpanId().isEmpty()) {
                roots.add(node);
            } else {
                TraceDAGNode parent = nodeMap.get(span.getParentSpanId());
                if (parent != null) {
                    parent.addChild(node);
                } else {
                    // Fragmented trace, treat as root for visibility
                    roots.add(node);
                }
            }
        }
        
        return roots;
    }
}
