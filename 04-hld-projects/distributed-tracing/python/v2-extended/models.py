from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    service_name: str
    operation_name: str
    start_time_ns: int
    duration_ns: int
    tags: Dict[str, str] = field(default_factory=dict)
    is_error: bool = False


class TraceDAGNode:
    def __init__(self, span: Span):
        self.span = span
        self.children: List['TraceDAGNode'] = []
        # Clock-skew adjusted timeline (v2 improvement #1), populated by
        # DAGAssembler.assemble; None until assembly runs.
        self.adjusted_start_ns: Optional[int] = None
        self.adjusted_end_ns: Optional[int] = None

    def add_child(self, child: 'TraceDAGNode'):
        self.children.append(child)
