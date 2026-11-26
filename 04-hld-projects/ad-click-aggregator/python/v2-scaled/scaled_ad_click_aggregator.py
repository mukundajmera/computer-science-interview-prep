import time
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

@dataclass
class ClickEvent:
    event_id: str
    campaign_id: str
    advertiser_id: str
    event_time_ms: int
    user_id: str = ""

@dataclass
class CorrectionAudit:
    event_id: str
    campaign_id: str
    advertiser_id: str
    original_event_time_ms: int
    corrected_at_ms: int
    delta: int

class PartitionedLog:
    def __init__(self, num_partitions: int = 4):
        self.num_partitions = num_partitions
        self.partitions: Dict[int, List[ClickEvent]] = {i: [] for i in range(num_partitions)}

    def get_partition(self, event_id: str) -> int:
        return hash(event_id) % self.num_partitions

    def append(self, event: ClickEvent):
        partition_id = self.get_partition(event.event_id)
        self.partitions[partition_id].append(event)

    def get_events(self, partition_id: int) -> List[ClickEvent]:
        return self.partitions[partition_id]

class ScaledAdClickAggregator:
    def __init__(self, late_event_bound_ms: int = 15 * 60 * 1000, dedup_retention_ms: int = 24 * 60 * 60 * 1000, num_partitions: int = 4):
        self.late_event_bound_ms = late_event_bound_ms
        self.dedup_retention_ms = dedup_retention_ms

        self.ingest_log = PartitionedLog(num_partitions)
        self.dedup_index: Dict[str, int] = {} # event_id -> ingest_time_ms
        self.watermark_ms = 0

        # campaign_id -> metrics
        self.campaign_clicks: Dict[str, int] = defaultdict(int)

        # Correction audit logs
        self.corrections: List[CorrectionAudit] = []

        self._current_time_ms_override = None

    def _get_current_time_ms(self) -> int:
        if self._current_time_ms_override is not None:
            return self._current_time_ms_override
        return int(time.time() * 1000)

    def set_time(self, current_time_ms: int):
        self._current_time_ms_override = current_time_ms

    def expire_dedup_index(self):
        current_time_ms = self._get_current_time_ms()
        to_delete = [
            event_id for event_id, ingest_time in self.dedup_index.items()
            if current_time_ms - ingest_time > self.dedup_retention_ms
        ]
        for event_id in to_delete:
            del self.dedup_index[event_id]

    def ingest_event(self, event: ClickEvent) -> bool:
        """
        Ingests a click event.
        Returns True if processed (or deduplicated idempotently), False if dropped (out of bounds).
        """
        current_time_ms = self._get_current_time_ms()

        # 1. Update watermark based on event time (we simulate watermark advancing with events)
        if event.event_time_ms > self.watermark_ms:
            self.watermark_ms = event.event_time_ms

        # 2. Check deduplication index
        if event.event_id in self.dedup_index:
            return True # Replay idempotence, treat as success but don't re-process

        # 3. Handle late/out-of-bounds events
        if event.event_time_ms < self.watermark_ms - self.late_event_bound_ms:
            # Out of bounds event, drop
            return False

        # 4. Append to partitioned immutable log
        self.ingest_log.append(event)

        # 5. Add to dedup index
        self.dedup_index[event.event_id] = current_time_ms

        # 6. Check if it's a correction (late but within bounds)
        # To determine if it's late, we can check against current watermark.
        # But really, any event arriving out of order could be considered a correction.
        # For simplicity, if it's strictly less than watermark, we count it as late correction delta.
        # Wait, if watermark is updated at step 1, it will never be strictly less if it advanced it.
        # So we check before step 1?
        # Actually, if it arrived with time < previous watermark, it's late.
        # Let's refine watermark logic: watermark is max observed event time.
        # The first check `if event.event_time_ms > self.watermark_ms` already did this.

        # It's a correction if its event_time_ms is less than the *current* watermark
        # which would only happen if it didn't advance the watermark just now.
        is_late = event.event_time_ms < self.watermark_ms

        # 7. Update aggregates
        self.campaign_clicks[event.campaign_id] += 1

        if is_late:
            self.corrections.append(CorrectionAudit(
                event_id=event.event_id,
                campaign_id=event.campaign_id,
                advertiser_id=event.advertiser_id,
                original_event_time_ms=event.event_time_ms,
                corrected_at_ms=current_time_ms,
                delta=1
            ))

        return True

    def get_campaign_clicks(self, campaign_id: str) -> int:
        return self.campaign_clicks.get(campaign_id, 0)

    def get_corrections(self) -> List[CorrectionAudit]:
        return self.corrections
