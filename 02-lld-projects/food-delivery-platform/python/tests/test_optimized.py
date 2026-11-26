import pytest
from v3_optimized.models import SurgePricingStrategy, Order, OrderState

def test_surge_pricing():
    strategy = SurgePricingStrategy()
    assert strategy.calculate_price(10.0, 3, 2) == 12.0
    assert strategy.calculate_price(10.0, 5, 2) == 15.0
    assert strategy.calculate_price(10.0, 5, 0) == 20.0

def test_order_state_transition():
    order = Order("O1", 10.0)
    
    order.transition_state(OrderState.CREATED, OrderState.ACCEPTED)
    assert order.state == OrderState.ACCEPTED
    
    with pytest.raises(ValueError):
        order.transition_state(OrderState.ACCEPTED, OrderState.DELIVERED)
