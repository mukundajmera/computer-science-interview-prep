import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v3-distributed"))
from regional_order_orchestrator import RegionalOrderOrchestrator


def test_orchestrator_can_be_constructed_without_hidden_state():
    orchestrator = RegionalOrderOrchestrator()
    assert orchestrator is not None


def test_create_regional_order_explicitly_reports_skeleton_status():
    with pytest.raises(NotImplementedError, match="V3 skeleton"):
        RegionalOrderOrchestrator().create_regional_order("user-1", 10.0, 20.0, "request-1")


def test_reconcile_failed_order_explicitly_reports_skeleton_status():
    with pytest.raises(NotImplementedError, match="V3 skeleton"):
        RegionalOrderOrchestrator().reconcile_failed_order("order-1", "payment_failed")
