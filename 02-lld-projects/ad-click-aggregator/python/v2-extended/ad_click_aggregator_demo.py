from in_memory_aggregation_store import InMemoryAggregationStore
from click_event import ClickEvent
from query_service import QueryService
from ad_click_aggregator import AdClickAggregator
from event_deduplicator import EventDeduplicator
from window_strategy import WindowStrategy
from fraud_rule import FraudRule

def main() -> None:
    store = InMemoryAggregationStore()
    deduplicator = EventDeduplicator()
    window_strategy = WindowStrategy(60000, 10000)
    fraud_rule = FraudRule()
    
    aggregator = AdClickAggregator(store, deduplicator, window_strategy, fraud_rule)
    query_service = QueryService(store)
    
    aggregator.ingest(ClickEvent("e1", "ad1", "u1", 1000))
    print(f"Clicks for ad1: {query_service.get_clicks_for_ad('ad1', 0)}")

if __name__ == "__main__":
    main()
