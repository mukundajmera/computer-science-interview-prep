from ad_click_aggregator import AdClickAggregator
from in_memory_aggregation_store import InMemoryAggregationStore
from query_service import QueryService
from click_event import ClickEvent


def main() -> None:
    store = InMemoryAggregationStore()
    aggregator = AdClickAggregator(store)
    query_service = QueryService(store)
    
    event = ClickEvent(event_id="e1", ad_id="ad1", user_id="u1", timestamp=1000)
    aggregator.ingest(event)
    
    print(f"Clicks for ad1: {query_service.get_clicks_for_ad('ad1', 0)}")


if __name__ == "__main__":
    main()
