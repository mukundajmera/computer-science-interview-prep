"""AdClickAggregator for ad-click-aggregator (v3-optimized)."""

from click_event import ClickEvent
from aggregation_key import AggregationKey
from sharded_state_store import ShardedStateStore
from watermark_manager import WatermarkManager
from late_event_handler import LateEventHandler
import time
from window_strategy import WindowStrategy
from event_deduplicator import EventDeduplicator

class AdClickAggregator:
    def __init__(self, store: ShardedStateStore, watermark_manager: WatermarkManager, late_handler: LateEventHandler, window_strategy: WindowStrategy, deduplicator: EventDeduplicator = None) -> None:
        self.store = store
        self.watermark_manager = watermark_manager
        self.late_handler = late_handler
        self.window_strategy = window_strategy
        self.deduplicator = deduplicator

    def ingest(self, event: ClickEvent, processing_time: int = None) -> None:
        if not event or not getattr(event, 'event_id', None) or not getattr(event, 'ad_id', None) or not getattr(event, 'user_id', None):
            raise ValueError("Empty input and invalid event payloads fail predictably")
         
        if processing_time is not None and processing_time - event.timestamp > 300000:
            return

        if self.deduplicator and self.deduplicator.is_duplicate(event.event_id):
            return

        self.watermark_manager.update_watermark(event.timestamp)
        
        if self.late_handler.is_late(event, self.watermark_manager.get_watermark()):
            return
            
        windows = self.window_strategy.get_overlapping_windows(event.timestamp)
        for window_start in windows:
            key = AggregationKey(event.ad_id, window_start)
            self.store.increment(key, 1)
