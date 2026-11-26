from sharded_state_store import ShardedStateStore
from watermark_manager import WatermarkManager
from late_event_handler import LateEventHandler
from window_strategy import WindowStrategy
from ad_click_aggregator import AdClickAggregator
from click_event import ClickEvent
from event_deduplicator import EventDeduplicator

def main() -> None:
    store = ShardedStateStore()
    watermark_manager = WatermarkManager()
    late_handler = LateEventHandler()
    window_strategy = WindowStrategy(60000, 10000)
    deduplicator = EventDeduplicator()
    
    aggregator = AdClickAggregator(store, watermark_manager, late_handler, window_strategy, deduplicator)
    
    aggregator.ingest(ClickEvent("e1", "ad1", "u1", 1000))

if __name__ == "__main__":
    main()
