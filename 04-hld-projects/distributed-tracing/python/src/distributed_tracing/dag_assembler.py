from typing import List, Dict
from .models import Span, TraceDAGNode

class DAGAssembler:
    def assemble(self, spans: List[Span]) -> List[TraceDAGNode]:
        node_map: Dict[str, TraceDAGNode] = {}
        roots: List[TraceDAGNode] = []

        for span in spans:
            node_map[span.span_id] = TraceDAGNode(span)

        for span in spans:
            node = node_map[span.span_id]
            if not span.parent_span_id:
                roots.append(node)
            else:
                parent = node_map.get(span.parent_span_id)
                if parent:
                    parent.add_child(node)
                else:
                    # Fragmented trace
                    roots.append(node)

        return roots
