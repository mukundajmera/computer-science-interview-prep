import sys
import os
import time
import threading
import pytest

# Dynamic sys.path insertion for the v1-basic implementation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

try:
    from token_streamer import StreamChunk, StreamingTokenAggregator
except ImportError:
    pass


def test_stream_aggregation_in_order():
    aggregator = StreamingTokenAggregator(max_size=10)
    
    chunks = [
        StreamChunk(index=0, text="Hello", is_final=False),
        StreamChunk(index=1, text=" world", is_final=False),
        StreamChunk(index=2, text="!", is_final=True, finish_reason="stop")
    ]
    
    for chunk in chunks:
        aggregator.write_chunk(chunk)
        
    result_stream = list(aggregator.read_stream(timeout_sec=0.1))
    
    assert result_stream == ["Hello", " world", "!"]
    assert aggregator._closed is True
    assert aggregator._dropped == 0


def test_sse_event_formatting():
    aggregator = StreamingTokenAggregator()
    
    formatted = aggregator.format_sse_event(event_type="message", data='{"text": "hello"}')
    expected = "event: message\ndata: {\"text\": \"hello\"}\n\n"
    assert formatted == expected
    
    # Test multi-line data
    formatted_multiline = aggregator.format_sse_event(event_type="update", data="line1\nline2")
    expected_multiline = "event: update\ndata: line1\ndata: line2\n\n"
    assert formatted_multiline == expected_multiline

def test_backpressure_slow_consumer():
    # Buffer size 2
    aggregator = StreamingTokenAggregator(max_size=2)
    
    chunks = [
        StreamChunk(index=0, text="1", is_final=False),
        StreamChunk(index=1, text="2", is_final=False),
        StreamChunk(index=2, text="3", is_final=False),
        StreamChunk(index=3, text="4", is_final=True)
    ]
    
    for chunk in chunks:
        aggregator.write_chunk(chunk)
        
    # Since max_size=2 and we wrote 4 chunks, 
    # it should have dropped the oldest ones ("1" and "2")
    # Buffer should contain "3" and "4"
    result_stream = list(aggregator.read_stream(timeout_sec=0.1))
    
    assert result_stream == ["3", "4"]
    assert aggregator._dropped == 2


def test_empty_and_final_chunk_handling():
    aggregator = StreamingTokenAggregator(max_size=5)
    
    aggregator.write_chunk(StreamChunk(index=0, text="", is_final=True, finish_reason="length"))
    
    result_stream = list(aggregator.read_stream(timeout_sec=0.1))
    
    assert result_stream == [""]
    assert aggregator._closed is True
    
    # Additional writes should be ignored after closed
    aggregator.write_chunk(StreamChunk(index=1, text="ignored", is_final=False))
    
    result_stream2 = list(aggregator.read_stream(timeout_sec=0.1))
    assert result_stream2 == []

def test_read_stream_timeout():
    aggregator = StreamingTokenAggregator(max_size=5)
    
    # Read from empty stream should timeout
    generator = aggregator.read_stream(timeout_sec=0.1)
    
    # Wait for the generator to yield or timeout
    start_time = time.time()
    items = list(generator)
    elapsed = time.time() - start_time
    
    assert items == []
    # Verify it took roughly timeout_sec to return (at least 0.05)
    assert elapsed >= 0.05
    
