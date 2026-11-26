import sys
import os
import pytest

# Insert v1-basic path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from matching_engine import MatchingEngine

def test_exact_price_match():
    engine = MatchingEngine()
    result1 = engine.place_order("1", "AAPL", False, 150, 100)
    assert len(result1.trades) == 0
    assert result1.residual_order is not None
    assert result1.residual_order.quantity == 100

    result2 = engine.place_order("2", "AAPL", True, 150, 100)
    assert len(result2.trades) == 1
    assert result2.trades[0].maker_order_id == "1"
    assert result2.trades[0].taker_order_id == "2"
    assert result2.trades[0].price == 150
    assert result2.trades[0].quantity == 100
    assert result2.residual_order is None
    
    assert not engine.get_asks_depth("AAPL")
    assert not engine.get_bids_depth("AAPL")

def test_partial_fill_multiple_resting_orders():
    engine = MatchingEngine()
    engine.place_order("1", "MSFT", False, 300, 50)
    result = engine.place_order("2", "MSFT", True, 300, 75)
    
    assert len(result.trades) == 1
    assert result.trades[0].quantity == 50
    assert result.residual_order is not None
    assert result.residual_order.quantity == 25
    
    bids = engine.get_bids_depth("MSFT")
    assert len(bids) == 1
    assert bids.get(300) == 25

def test_price_time_priority_ordering():
    engine = MatchingEngine()
    engine.place_order("1", "GOOG", False, 2800, 10)
    engine.place_order("2", "GOOG", False, 2790, 15)
    engine.place_order("3", "GOOG", False, 2800, 20)
    
    result = engine.place_order("4", "GOOG", True, 2800, 30)
    
    assert len(result.trades) == 3
    
    # Should execute best price first (2790)
    assert result.trades[0].maker_order_id == "2"
    assert result.trades[0].quantity == 15
    assert result.trades[0].price == 2790
    
    # Then at 2800, execute in time priority (order 1 before order 3)
    assert result.trades[1].maker_order_id == "1"
    assert result.trades[1].quantity == 10
    assert result.trades[1].price == 2800
    
    assert result.trades[2].maker_order_id == "3"
    assert result.trades[2].quantity == 5
    assert result.trades[2].price == 2800
    
    assert result.residual_order is None

def test_order_cancellation():
    engine = MatchingEngine()
    engine.place_order("1", "TSLA", True, 800, 50)
    engine.place_order("2", "TSLA", True, 800, 30)
    
    depth_before = engine.get_bids_depth("TSLA")
    assert depth_before.get(800) == 80
    
    assert engine.cancel_order("TSLA", "1") is True
    
    depth_after = engine.get_bids_depth("TSLA")
    assert depth_after.get(800) == 30
    
    assert engine.cancel_order("TSLA", "1") is False

def test_deterministic_sequence_ordering():
    engine = MatchingEngine()
    r1 = engine.place_order("1", "AMZN", True, 3300, 10)
    r2 = engine.place_order("2", "AMZN", True, 3300, 10)
    
    assert r1.residual_order.sequence_number == 1
    assert r2.residual_order.sequence_number == 2
