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
    
    def add_child(self, child: 'TraceDAGNode'):
        self.children.append(child)
