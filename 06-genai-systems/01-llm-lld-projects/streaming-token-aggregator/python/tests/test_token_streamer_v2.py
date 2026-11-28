import itertools
import os
import sys
import threading
import time

import pytest

# Dynamic sys.path insertion for the v2-extended implementation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from token_streamer_v2 import StreamChunk, StreamingTokenAggregator


def write_all(aggregator, texts, final_index=None, start=0):
    for offset, text in enumerate(texts):
        index = start + offset
        aggregator.write_chunk(StreamChunk(
            index=index, text=text,
            is_final=(index == final_index),
            finish_reason="stop" if index == final_index else None))


# --- v1 fixture parity (names and default semantics kept) ---

def test_stream_aggregation_in_order():
    aggregator = StreamingTokenAggregator(max_size=10)
    write_all(aggregator, ["Hello", " world", "!"], final_index=2)
    assert list(aggregator.read_stream(timeout_sec=0.1)) == ["Hello", " world", "!"]
    assert aggregator._closed is True
    assert aggregator._dropped == 0


def test_sse_event_formatting():
    aggregator = StreamingTokenAggregator()
    formatted = aggregator.format_sse_event(event_type="message", data='{"text": "hello"}')
    assert formatted == "event: message\ndata: {\"text\": \"hello\"}\n\n"
    multiline = aggregator.format_sse_event(event_type="update", data="line1\nline2")
    assert multiline == "event: update\ndata: line1\ndata: line2\n\n"


def test_backpressure_slow_consumer():
    aggregator = StreamingTokenAggregator(max_size=2)
    write_all(aggregator, ["1", "2", "3", "4"], final_index=3)
    assert list(aggregator.read_stream(timeout_sec=0.1)) == ["3", "4"]
    assert aggregator._dropped == 2


def test_empty_and_final_chunk_handling():
    aggregator = StreamingTokenAggregator(max_size=5)
    aggregator.write_chunk(StreamChunk(index=0, text="", is_final=True, finish_reason="length"))
    assert list(aggregator.read_stream(timeout_sec=0.1)) == [""]
    assert aggregator._closed is True
    aggregator.write_chunk(StreamChunk(index=1, text="ignored", is_final=False))
    assert list(aggregator.read_stream(timeout_sec=0.1)) == []


def test_read_stream_timeout():
    aggregator = StreamingTokenAggregator(max_size=5)
    start_time = time.monotonic()
    items = list(aggregator.read_stream(timeout_sec=0.1))
    elapsed = time.monotonic() - start_time
    assert items == []
    assert elapsed >= 0.05


# --- v2: cancellation propagation (FOLLOW-UPS 2) ---

def test_cancel_unblocks_waiting_consumer():
    aggregator = StreamingTokenAggregator(max_size=5)
    items = []

    def consumer():
        items.extend(aggregator.read_stream(timeout_sec=5.0))

    thread = threading.Thread(target=consumer)
    start = time.monotonic()
    thread.start()
    time.sleep(0.2)
    aggregator.cancel(reason="client disconnected")
    thread.join(timeout=2.0)
    elapsed = time.monotonic() - start

    assert not thread.is_alive()
    assert elapsed < 2.0  # unblocked long before the 5s timeout
    assert items == []


def test_writes_after_cancel_ignored_and_flagged():
    aggregator = StreamingTokenAggregator(max_size=5)
    assert aggregator.is_cancelled is False
    aggregator.cancel(reason="tab closed")
    aggregator.cancel(reason="duplicate is harmless")

    assert aggregator.is_cancelled is True
    assert aggregator.cancel_reason == "tab closed"
    aggregator.write_chunk(StreamChunk(index=0, text="late", is_final=False))
    assert list(aggregator.read_stream(timeout_sec=0.1)) == []
    assert aggregator.metrics()["written"] == 0
    assert aggregator.metrics()["cancelled"] is True


# --- v2: Last-Event-ID replay (FOLLOW-UPS 3) ---

def test_replay_after_reconnect_with_last_event_id():
    aggregator = StreamingTokenAggregator(max_size=10, replay_capacity=10)
    write_all(aggregator, ["t0", "t1", "t2", "t3", "t4"], final_index=4)

    # First connection reads two chunks, then drops.
    first = itertools.islice(aggregator.read_stream(timeout_sec=0.1), 2)
    assert list(first) == ["t0", "t1"]

    # Reconnect with Last-Event-ID=1: replay misses nothing, duplicates nothing.
    resumed = list(aggregator.read_stream(timeout_sec=0.1, last_event_id=1))
    assert resumed == ["t2", "t3", "t4"]
    assert aggregator.metrics()["replayed"] == 3


def test_replay_window_is_bounded():
    aggregator = StreamingTokenAggregator(max_size=10, replay_capacity=3)
    write_all(aggregator, ["t0", "t1", "t2", "t3", "t4", "t5"], final_index=5)

    # Only the last 3 chunks are retained; an older Last-Event-ID resumes from
    # the oldest retained chunk (documented best-effort, not silent).
    resumed = list(aggregator.read_stream(timeout_sec=0.1, last_event_id=0))
    assert resumed == ["t3", "t4", "t5"]
    assert aggregator.metrics()["replayed"] == 3


def test_default_retain_nothing_preserves_ephemeral_boundary():
    aggregator = StreamingTokenAggregator(max_size=10)  # replay_capacity=0
    write_all(aggregator, ["t0", "t1"], final_index=1)
    list(aggregator.read_stream(timeout_sec=0.1))
    assert len(aggregator._history) == 0
    resumed = list(aggregator.read_stream(timeout_sec=0.1, last_event_id=0))
    assert resumed == []
    assert aggregator.metrics()["replayed"] == 0


# --- v2: SSE id field ---

def test_sse_event_id_field():
    aggregator = StreamingTokenAggregator()
    formatted = aggregator.format_sse_event(event_type="message", data="hello", event_id=7)
    assert formatted == "id: 7\nevent: message\ndata: hello\n\n"
    # Omitting event_id yields exactly the v1 format.
    assert aggregator.format_sse_event("message", "hello") == "event: message\ndata: hello\n\n"


# --- v2: metrics and hardening ---

def test_metrics_snapshot_counts():
    aggregator = StreamingTokenAggregator(max_size=2)
    write_all(aggregator, ["1", "2", "3", "4"], final_index=3)
    assert list(aggregator.read_stream(timeout_sec=0.1)) == ["3", "4"]
    snapshot = aggregator.metrics()
    assert snapshot["written"] == 4
    assert snapshot["read"] == 2
    assert snapshot["dropped"] == 2
    assert snapshot["replayed"] == 0
    assert snapshot["buffered"] == 0
    assert snapshot["closed"] is True
    assert snapshot["cancelled"] is False


def test_constructor_validation():
    with pytest.raises(ValueError, match="max_size must be a positive integer"):
        StreamingTokenAggregator(max_size=0)
    with pytest.raises(ValueError, match="max_size must be a positive integer"):
        StreamingTokenAggregator(max_size=-3)
    with pytest.raises(ValueError, match="replay_capacity must be a non-negative integer"):
        StreamingTokenAggregator(max_size=5, replay_capacity=-1)


def test_read_on_cancelled_stream_ends_promptly():
    aggregator = StreamingTokenAggregator(max_size=5)
    aggregator.cancel()
    start = time.monotonic()
    assert list(aggregator.read_stream(timeout_sec=5.0)) == []
    assert time.monotonic() - start < 1.0
