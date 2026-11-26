import pytest
from v1_basic.models import Menu, MenuItem, Cart, Order, OrderState

def test_menu_and_cart():
    menu = Menu()
    item = MenuItem("1", "Burger", 10.0)
    menu.add_item(item)
    
    cart = Cart()
    cart.add_item(item)
    
    assert len(cart.items) == 1
    assert cart.get_total() == 10.0

def test_order_state():
    order = Order("O1", [], 10.0)
    assert order.state == OrderState.CREATED
    order.set_state(OrderState.RESERVATION)
    assert order.state == OrderState.RESERVATION
