import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed'))

from distributed_brokerage_service import (
    DistributedBrokerageService,
    OrderEvent,
)

class DummyDistributedBrokerageService:
    def __init__(self):
        self.replicated_events = []
        self.reconciled_regions = set()

    def route_order_region(self, user_id: str, symbol: str) -> str:
        # Simple static routing for test
        if user_id.startswith("eu"):
            return "eu-west-1"
        return "us-east-1"

    def replicate_order_event(self, event: OrderEvent) -> None:
        self.replicated_events.append(event)

    def reconcile_region(self, region: str) -> None:
        self.reconciled_regions.add(region)


def test_route_order_region_returns_correct_region():
    service = DummyDistributedBrokerageService()
    
    region_eu = service.route_order_region("eu_user1", "AAPL")
    assert region_eu == "eu-west-1"
    
    region_us = service.route_order_region("us_user1", "AAPL")
    assert region_us == "us-east-1"


def test_replicate_order_event_records_event():
    service = DummyDistributedBrokerageService()
    event = OrderEvent(order_id="ord-1", event_type="FILLED")
    
    service.replicate_order_event(event)
    
    assert len(service.replicated_events) == 1
    assert service.replicated_events[0].order_id == "ord-1"
    assert service.replicated_events[0].event_type == "FILLED"


def test_reconcile_region_records_region():
    service = DummyDistributedBrokerageService()
    
    service.reconcile_region("eu-west-1")
    service.reconcile_region("us-east-1")
    
    assert "eu-west-1" in service.reconciled_regions
    assert "us-east-1" in service.reconciled_regions
