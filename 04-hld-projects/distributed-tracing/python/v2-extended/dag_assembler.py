"""v2-extended distributed tracing: DAG assembly.

Improvements over v1-basic (each has dedicated tests; the same three are
named in tail_sampler.py, the other main class):

1. Clock-skew adjustment (FOLLOW-UPS.md #1, PITFALLS "Forgetting Clock
   Skew"): after assembly every node gets an adjusted timeline clamped
   inside its parent's boundaries, since timestamps from different servers
   cannot be trusted to align.

2. Deduplication of at-least-once replays (PITFALLS "Omitting
   Deduplication for At-Least-Once Kafka Replays"): spans are deduplicated
   on span_id during assembly so a replayed span never appears twice in
   the DAG.

3. Windowed tail sampling with late-span fragments (FOLLOW-UPS.md #3):
   implemented in tail_sampler.py.
"""
from typing import Dict, List, Set
from .models import Span, TraceDAGNode


class DAGAssembler:
    def assemble(self, spans: List[Span]) -> List[TraceDAGNode]:
        node_map: Dict[str, TraceDAGNode] = {}
        unique_spans: List[Span] = []
        seen_ids: Set[str] = set()

        # Improvement #2: drop exact replays before building the tree.
        for span in spans:
            if span.span_id in seen_ids:
                continue
            seen_ids.add(span.span_id)
            unique_spans.append(span)
            node_map[span.span_id] = TraceDAGNode(span)

        roots: List[TraceDAGNode] = []
        for span in unique_spans:
            node = node_map[span.span_id]
            # A span that names itself as parent is malformed; treat it as a
            # root so the tree can never self-loop. A missing parent is a
            # fragmented trace, also surfaced as a root for visibility.
            if (not span.parent_span_id
                    or span.parent_span_id == span.span_id
                    or span.parent_span_id not in node_map):
                roots.append(node)
            else:
                node_map[span.parent_span_id].add_child(node)

        # Improvement #1: causal clamping of child timelines. Recursion from
        # roots cannot cycle: every node has at most one parent, so any
        # cycle's members all have parents and none is reachable from a root.
        for root in roots:
            self._adjust_clock_skew(root)

        return roots

    def _adjust_clock_skew(self, node: TraceDAGNode):
        span = node.span
        node.adjusted_start_ns = span.start_time_ns
        node.adjusted_end_ns = span.start_time_ns + span.duration_ns

        for child in node.children:
            self._adjust_clock_skew(child)
            # A child causally cannot start before its parent or end after
            # it; clamp the child's timeline into the parent's boundaries.
            child.adjusted_start_ns = min(
                max(child.adjusted_start_ns, node.adjusted_start_ns),
                node.adjusted_end_ns)
            child.adjusted_end_ns = min(
                max(child.adjusted_end_ns, child.adjusted_start_ns),
                node.adjusted_end_ns)
