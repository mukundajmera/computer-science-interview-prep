package v2_extended;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * v2-extended distributed tracing: DAG assembly.
 *
 * Improvements over v1-basic (each has dedicated tests; the same three are
 * named in TailSampler, the other main class):
 *
 * 1. Clock-skew adjustment (FOLLOW-UPS.md #1, PITFALLS "Forgetting Clock
 *    Skew"): after assembly every node gets an adjusted timeline clamped
 *    inside its parent's boundaries, since timestamps from different
 *    servers cannot be trusted to align.
 *
 * 2. Deduplication of at-least-once replays (PITFALLS "Omitting
 *    Deduplication for At-Least-Once Kafka Replays"): spans are
 *    deduplicated on span_id during assembly so a replayed span never
 *    appears twice in the DAG.
 *
 * 3. Windowed tail sampling with late-span fragments (FOLLOW-UPS.md #3):
 *    implemented in TailSampler.
 */
public class DAGAssembler {

    public List<TraceDAGNode> assemble(List<Span> spans) {
        Map<String, TraceDAGNode> nodeMap = new HashMap<>();
        List<Span> uniqueSpans = new ArrayList<>();
        Set<String> seenIds = new HashSet<>();

        // Improvement #2: drop exact replays before building the tree.
        for (Span span : spans) {
            if (seenIds.add(span.getSpanId())) {
                uniqueSpans.add(span);
                nodeMap.put(span.getSpanId(), new TraceDAGNode(span));
            }
        }

        List<TraceDAGNode> roots = new ArrayList<>();
        for (Span span : uniqueSpans) {
            TraceDAGNode node = nodeMap.get(span.getSpanId());
            String parentId = span.getParentSpanId();
            // A span that names itself as parent is malformed; treat it as a
            // root so the tree can never self-loop. A missing parent is a
            // fragmented trace, also surfaced as a root for visibility.
            if (parentId == null || parentId.isEmpty()
                    || parentId.equals(span.getSpanId())
                    || !nodeMap.containsKey(parentId)) {
                roots.add(node);
            } else {
                nodeMap.get(parentId).addChild(node);
            }
        }

        // Improvement #1: causal clamping of child timelines. Recursion from
        // roots cannot cycle: every node has at most one parent, so any
        // cycle's members all have parents and none is reachable from a root.
        for (TraceDAGNode root : roots) {
            adjustClockSkew(root);
        }

        return roots;
    }

    private void adjustClockSkew(TraceDAGNode node) {
        for (TraceDAGNode child : node.getChildren()) {
            adjustClockSkew(child);
            // A child causally cannot start before its parent or end after
            // it; clamp the child's timeline into the parent's boundaries.
            child.setAdjustedStartNs(Math.min(
                    Math.max(child.getAdjustedStartNs(), node.getAdjustedStartNs()),
                    node.getAdjustedEndNs()));
            child.setAdjustedEndNs(Math.min(
                    Math.max(child.getAdjustedEndNs(), child.getAdjustedStartNs()),
                    node.getAdjustedEndNs()));
        }
    }
}
