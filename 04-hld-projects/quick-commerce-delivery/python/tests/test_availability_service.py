import os
import sys
from datetime import datetime

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v1-basic"))
from availability_service import AvailabilityItem, AvailabilityService, OrderLine


def test_availability_item_preserves_inventory_fields():
    item = AvailabilityItem("item-1", "center-1", 4, 15)
    assert item.item_id == "item-1"
    assert item.center_id == "center-1"
    assert item.available_qty == 4
    assert item.eta_minutes == 15


def test_order_line_preserves_requested_quantity():
    line = OrderLine("item-1", 2)
    assert line.item_id == "item-1"
    assert line.qty == 2


def test_v1_service_methods_explicitly_report_skeleton_status():
    service = AvailabilityService()
    with pytest.raises(NotImplementedError, match="V1 skeleton"):
        service.lookup(10.0, 20.0, "item-1", 1, 10)
    with pytest.raises(NotImplementedError, match="V1 skeleton"):
        service.place_order("user-1", 10.0, 20.0, [OrderLine("item-1", 1)], "request-1")
