from typing import List, Dict
from collections import defaultdict
from .models import Span

class TailSampler:
    def __init__(self, latency_threshold_ns: int):
        self.latency_threshold_ns = latency_threshold_ns
        self.buffers: Dict[str, List[Span]] = defaultdict(list)

    def ingest(self, span: Span):
        self.buffers[span.trace_id].append(span)

    def evaluate_window(self, trace_id: str) -> List[Span]:
        spans = self.buffers.pop(trace_id, [])
        if not spans:
            return []

        keep = False
        max_duration = 0

        for span in spans:
            if span.is_error:
                keep = True
                break
            if span.duration_ns > max_duration:
                max_duration = span.duration_ns

        if not keep and max_duration > self.latency_threshold_ns:
            keep = True

        return spans if keep else []
    
    def crash(self):
        self.buffers.clear()
