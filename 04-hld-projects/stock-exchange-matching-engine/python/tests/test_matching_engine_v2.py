import sys
import os
import pytest

# Insert v2-extended path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from matching_engine_v2 import MarketDataPublisherV2, MatchingEngineV2


# ---------- v1 parity: every v1 behavior still holds on the v2 track ----------

def test_exact_price_match():
    engine = MatchingEngineV2()
    result1 = engine.place_order("1", "AAPL", False, 150, 100)
    assert len(result1.trades) == 0
    assert result1.residual_order is not None
    assert result1.residual_order.quantity == 100
    assert result1.status == "resting"

    result2 = engine.place_order("2", "AAPL", True, 150, 100)
    assert len(result2.trades) == 1
    assert result2.trades[0].maker_order_id == "1"
    assert result2.trades[0].taker_order_id == "2"
    assert result2.trades[0].price == 150
    assert result2.trades[0].quantity == 100
    assert result2.residual_order is None
    assert result2.status == "filled"

    assert not engine.get_asks_depth("AAPL")
    assert not engine.get_bids_depth("AAPL")


def test_partial_fill_multiple_resting_orders():
    engine = MatchingEngineV2()
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
    engine = MatchingEngineV2()
    engine.place_order("1", "GOOG", False, 2800, 10)
    engine.place_order("2", "GOOG", False, 2790, 15)
    engine.place_order("3", "GOOG", False, 2800, 20)

    result = engine.place_order("4", "GOOG", True, 2800, 30)

    assert len(result.trades) == 3
    assert result.trades[0].maker_order_id == "2"
    assert result.trades[0].quantity == 15
    assert result.trades[0].price == 2790
    assert result.trades[1].maker_order_id == "1"
    assert result.trades[1].quantity == 10
    assert result.trades[1].price == 2800
    assert result.trades[2].maker_order_id == "3"
    assert result.trades[2].quantity == 5
    assert result.trades[2].price == 2800
    assert result.residual_order is None


def test_order_cancellation():
    engine = MatchingEngineV2()
    engine.place_order("1", "TSLA", True, 800, 50)
    engine.place_order("2", "TSLA", True, 800, 30)

    depth_before = engine.get_bids_depth("TSLA")
    assert depth_before.get(800) == 80

    assert engine.cancel_order("TSLA", "1") is True

    depth_after = engine.get_bids_depth("TSLA")
    assert depth_after.get(800) == 30

    assert engine.cancel_order("TSLA", "1") is False


def test_deterministic_sequence_ordering():
    engine = MatchingEngineV2()
    r1 = engine.place_order("1", "AMZN", True, 3300, 10)
    r2 = engine.place_order("2", "AMZN", True, 3300, 10)

    assert r1.residual_order.sequence_number == 1
    assert r2.residual_order.sequence_number == 2


# ---------- v2 improvement 2: order validation ----------

def test_rejects_non_positive_price():
    engine = MatchingEngineV2()
    result = engine.place_order("1", "AAPL", True, 0, 100)

    assert result.status == "rejected"
    assert result.reject_reason == "non-positive price"
    assert result.residual_order is None
    assert engine.get_bids_depth("AAPL") == {}
    # A rejected order never reaches the book, so it cannot be cancelled.
    assert engine.cancel_order("AAPL", "1") is False


def test_rejects_non_positive_quantity():
    engine = MatchingEngineV2()
    result = engine.place_order("1", "AAPL", False, 150, -5)

    assert result.status == "rejected"
    assert result.reject_reason == "non-positive quantity"
    assert engine.get_asks_depth("AAPL") == {}


def test_rejects_duplicate_order_id():
    engine = MatchingEngineV2()
    first = engine.place_order("1", "AAPL", True, 150, 100)
    assert first.status == "resting"

    duplicate = engine.place_order("1", "AAPL", True, 155, 50)
    assert duplicate.status == "rejected"
    assert duplicate.reject_reason == "duplicate order id"

    # Book still holds exactly the first order.
    assert engine.get_bids_depth("AAPL") == {150: 100}


def test_rejections_are_logged_with_reason():
    engine = MatchingEngineV2()
    engine.place_order("1", "AAPL", True, 0, 100)

    assert len(engine.event_log) == 1
    event = engine.event_log[0]
    assert event["op"] == "place"
    assert event["accepted"] is False
    assert event["reason"] == "non-positive price"
    assert event["sequence"] == 1


# ---------- v2 improvement 1: sequenced event log + replay ----------

def test_replay_reproduces_identical_book_state():
    engine = MatchingEngineV2()
    engine.place_order("1", "AAPL", False, 150, 100)
    engine.place_order("2", "AAPL", False, 151, 50)
    engine.place_order("3", "AAPL", True, 150, 40)   # matches 40 of order 1
    engine.place_order("4", "AAPL", True, 149, 200)  # rests
    engine.cancel_order("AAPL", "2")

    standby = MatchingEngineV2.replay(engine.event_log)

    assert standby.get_bids_depth("AAPL") == engine.get_bids_depth("AAPL")
    assert standby.get_asks_depth("AAPL") == engine.get_asks_depth("AAPL")
    assert standby.get_asks_depth("AAPL") == {150: 60}
    assert standby.get_bids_depth("AAPL") == {149: 200}


def test_replay_continues_sequencing_past_log_maximum():
    engine = MatchingEngineV2()
    engine.place_order("1", "AMZN", True, 3300, 10)
    engine.place_order("2", "AMZN", True, 3300, 10)
    max_logged = max(e["sequence"] for e in engine.event_log)

    standby = MatchingEngineV2.replay(engine.event_log)
    fresh = standby.place_order("3", "AMZN", True, 3300, 10)

    assert fresh.residual_order.sequence_number > max_logged
    # Same FIFO depth on both engines.
    assert standby.get_bids_depth("AMZN") == {3300: 30}


def test_replay_skips_rejected_and_failed_events():
    engine = MatchingEngineV2()
    engine.place_order("1", "TSLA", True, 0, 50)      # rejected
    engine.place_order("2", "TSLA", True, 800, 50)    # rests
    engine.cancel_order("TSLA", "nope")               # failed cancel
    engine.cancel_order("TSLA", "2")                  # successful cancel

    standby = MatchingEngineV2.replay(engine.event_log)

    assert standby.get_bids_depth("TSLA") == {}
    assert standby.get_bids_depth("TSLA") == engine.get_bids_depth("TSLA")


# ---------- v2 improvement 3: slow-consumer-safe market data ----------

def test_slow_consumer_drops_are_counted_and_isolated():
    publisher = MarketDataPublisherV2()
    publisher.subscribe("fast", max_queue=10)
    publisher.subscribe("slow", max_queue=2)

    engine = MatchingEngineV2(publisher=publisher)
    # Three resting asks, then three buys -> 3 trades published.
    engine.place_order("s1", "AAPL", False, 150, 10)
    engine.place_order("s2", "AAPL", False, 151, 10)
    engine.place_order("s3", "AAPL", False, 152, 10)
    engine.place_order("b1", "AAPL", True, 152, 10)
    engine.place_order("b2", "AAPL", True, 152, 10)
    engine.place_order("b3", "AAPL", True, 152, 10)

    # Fast consumer drains everything: 3 trades.
    received = 0
    while publisher.poll("fast") is not None:
        received += 1
    assert received == 3

    # Slow consumer held only its first 2; the third was dropped for it only.
    assert publisher.pending("slow") == 2
    assert publisher.dropped("slow") == 1
    assert publisher.dropped("fast") == 0
