import os
import sys
from datetime import datetime

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2-scaled"))
from cached_availability_service import CachedAvailabilityService, InventoryDelta


def test_inventory_delta_preserves_event_data():
    observed = datetime(2026, 1, 1)
    delta = InventoryDelta("center-1", "item-1", 3, observed)
    assert delta.center_id == "center-1"
    assert delta.item_id == "item-1"
    assert delta.available_qty == 3
    assert delta.observed_at == observed


def test_inventory_delta_supports_zero_inventory_events():
    delta = InventoryDelta("center-1", "item-1", 0, datetime.now())
    assert delta.available_qty == 0


def test_v2_service_methods_explicitly_report_skeleton_status():
    service = CachedAvailabilityService()
    with pytest.raises(NotImplementedError, match="V2 skeleton"):
        service.search(10.0, 20.0, "item-1", 1, 10)
    with pytest.raises(NotImplementedError, match="V2 skeleton"):
        service.on_inventory_delta(InventoryDelta("center-1", "item-1", 0, datetime.now()))
