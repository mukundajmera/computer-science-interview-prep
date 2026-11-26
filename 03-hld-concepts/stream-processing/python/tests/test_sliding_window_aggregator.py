import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from sliding_window_aggregator import SlidingWindowAggregator, sum_aggregation, count_aggregation
from dataclasses import dataclass

@dataclass
class SimpleEvent:
    timestamp: int
    value: float

def extract_timestamp(e: SimpleEvent) -> int:
    return e.timestamp

def test_tumbling_windows():
    create_acc, add_fn, get_res = sum_aggregation()

    agg = SlidingWindowAggregator(
        window_size=10,
        slide_size=10,
        allowed_lateness=0,
        timestamp_extractor=extract_timestamp,
        create_accumulator=create_acc,
        add_fn=add_fn,
        get_result_fn=get_res
    )

    agg.process_event(SimpleEvent(2, 5.0))
    agg.process_event(SimpleEvent(7, 10.0))
    agg.process_event(SimpleEvent(12, 2.0))

    res = agg.advance_watermark(10)
    assert len(res) == 1
    assert res[0].start == 0
    assert res[0].end == 10
    assert res[0].result == 15.0

    res = agg.advance_watermark(20)
    assert len(res) == 1
    assert res[0].start == 10
    assert res[0].end == 20
    assert res[0].result == 2.0

def test_sliding_windows():
    create_acc, add_fn, get_res = sum_aggregation()

    agg = SlidingWindowAggregator(
        window_size=10,
        slide_size=5,
        allowed_lateness=0,
        timestamp_extractor=extract_timestamp,
        create_accumulator=create_acc,
        add_fn=add_fn,
        get_result_fn=get_res
    )

    agg.process_event(SimpleEvent(7, 5.0))

    res = agg.advance_watermark(11)
    assert len(res) == 1
    assert res[0].start == 0
    assert res[0].end == 10
    assert res[0].result == 5.0

    res = agg.advance_watermark(16)
    assert len(res) == 1
    assert res[0].start == 5
    assert res[0].end == 15
    assert res[0].result == 5.0

def test_late_event_handling():
    create_acc, add_fn, get_res = sum_aggregation()

    agg = SlidingWindowAggregator(
        window_size=10,
        slide_size=10,
        allowed_lateness=5,
        timestamp_extractor=extract_timestamp,
        create_accumulator=create_acc,
        add_fn=add_fn,
        get_result_fn=get_res
    )

    agg.process_event(SimpleEvent(2, 10.0))
    agg.advance_watermark(11) # Window 0-10 not closed yet because lateness=5

    # Event t=7, watermark=11, lateness=5 -> 7 < 11-5 is False, so it's accepted.
    agg.process_event(SimpleEvent(7, 5.0))

    res = agg.advance_watermark(15) # Watermark is 15 >= 10+5, so 0-10 is closed
    assert len(res) == 1
    assert res[0].start == 0
    assert res[0].end == 10
    assert res[0].result == 15.0

    agg.process_event(SimpleEvent(3, 20.0))

    res = agg.advance_watermark(20)
    assert len(res) == 0

def test_count_aggregation():
    create_acc, add_fn, get_res = count_aggregation()

    agg = SlidingWindowAggregator(
        window_size=10,
        slide_size=10,
        allowed_lateness=0,
        timestamp_extractor=extract_timestamp,
        create_accumulator=create_acc,
        add_fn=add_fn,
        get_result_fn=get_res
    )

    agg.process_event(SimpleEvent(1, 100))
    agg.process_event(SimpleEvent(2, 200))
    agg.process_event(SimpleEvent(5, 300))

    res = agg.advance_watermark(10)
    assert len(res) == 1
    assert res[0].result == 3
