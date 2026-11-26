import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from simple_producer_consumer import SimpleProducerConsumer

def test_produce_and_consume():
    stream = SimpleProducerConsumer(3)
    key = "test-key"
    message = "test-message"
    
    partition = stream.partition_for_key(key)
    p = stream.produce(key, message)
    
    assert p == partition
    assert stream.consume(partition) == message
    assert stream.current_offset(partition) == 1

def test_consume_empty_partition_returns_none():
    stream = SimpleProducerConsumer(3)
    
    assert stream.consume(0) is None
    assert stream.current_offset(0) == 0

def test_invalid_partition_count_raises_value_error():
    with pytest.raises(ValueError, match="partition_count must be > 0"):
        SimpleProducerConsumer(0)
    with pytest.raises(ValueError, match="partition_count must be > 0"):
        SimpleProducerConsumer(-1)

def test_different_keys_may_map_to_different_partitions():
    stream = SimpleProducerConsumer(3)
    
    stream.produce("key1", "msg1")
    stream.produce("key2", "msg2")
    stream.produce("key3", "msg3")
    
    p1 = stream.partition_for_key("key1")
    p2 = stream.partition_for_key("key2")
    p3 = stream.partition_for_key("key3")
    
    assert stream.consume(p1) == "msg1"
    assert stream.consume(p2) == "msg2"
    assert stream.consume(p3) == "msg3"
