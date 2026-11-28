"""v2-extended distributed tracing: tail-based sampling.

Improvements over v1-basic (each has dedicated tests; the same three are
named in dag_assembler.py, the other main class):

1. Clock-skew adjustment: implemented in dag_assembler.py (FOLLOW-UPS.md
   #1, PITFALLS "Forgetting Clock Skew").

2. Deduplication of at-least-once replays (PITFALLS "Omitting
   Deduplication for At-Least-Once Kafka Replays"): ingest() drops spans
   whose (trace_id, span_id) is already buffered and reports the duplicate,
   so a Kafka replay after a worker restart never double-counts a span.

3. Windowed sampling with an injectable clock and late-span fragments
   (FOLLOW-UPS.md #3): buffers expire after window_ns (default 30s, like
   the design doc's buffering window) via flush_expired(), and a span that
   arrives after its trace's window closed opens a fresh buffer, evaluated
   on its own merits as a fragment.
"""
import time
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Set, Tuple
from .models import Span


class TailSampler:
    def __init__(self, latency_threshold_ns: int, window_ns: int = 30_000_000_000,
                 clock: Optional[Callable[[], int]] = None):
        self.latency_threshold_ns = latency_threshold_ns
        self.window_ns = window_ns
        self.clock = clock or time.monotonic_ns
        self.buffers: Dict[str, List[Span]] = defaultdict(list)
        self.first_seen_ns: Dict[str, int] = {}
        self._seen_ids: Set[Tuple[str, str]] = set()

    def ingest(self, span: Span) -> bool:
        """Buffers the span. Returns False without buffering when the span is
        an at-least-once replay duplicate (improvement #2)."""
        key = (span.trace_id, span.span_id)
        if key in self._seen_ids:
            return False
        self._seen_ids.add(key)
        if span.trace_id not in self.first_seen_ns:
            self.first_seen_ns[span.trace_id] = self.clock()
        self.buffers[span.trace_id].append(span)
        return True

    def _should_keep(self, spans: List[Span]) -> bool:
        max_duration = 0
        for span in spans:
            if span.is_error:
                return True
            if span.duration_ns > max_duration:
                max_duration = span.duration_ns
        return max_duration > self.latency_threshold_ns

    def evaluate_window(self, trace_id: str) -> List[Span]:
        """Closes the buffer for trace_id and applies the keep/drop decision.
        After this, the trace's dedup memory is released, so a late-arriving
        span opens a fresh fragment buffer (improvement #3)."""
        spans = self.buffers.pop(trace_id, [])
        self.first_seen_ns.pop(trace_id, None)
        self._seen_ids = {k for k in self._seen_ids if k[0] != trace_id}
        if not spans:
            return []
        return spans if self._should_keep(spans) else []

    def flush_expired(self) -> Dict[str, List[Span]]:
        """Evaluates every buffer whose window has elapsed (improvement #3).
        Returns trace_id -> kept spans (empty list for dropped traces)."""
        now = self.clock()
        expired = [tid for tid, t0 in self.first_seen_ns.items()
                   if now - t0 >= self.window_ns]
        return {tid: self.evaluate_window(tid) for tid in expired}

    def crash(self):
        """Worker crash: in-memory buffers, window timestamps and dedup state
        are all lost (PITFALLS "Ignoring In-Memory Tail-Sampling Loss")."""
        self.buffers.clear()
        self.first_seen_ns.clear()
        self._seen_ids.clear()
