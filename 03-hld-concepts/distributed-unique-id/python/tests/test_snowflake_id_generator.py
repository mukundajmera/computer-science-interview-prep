import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from snowflake_id_generator import SnowflakeIdGenerator, ClockMovedBackwardsException

CUSTOM_EPOCH = 1609459200000

def test_monotonicity():
    generator = SnowflakeIdGenerator(1, 1, CUSTOM_EPOCH, 5)
    id1 = generator.next_id()
    id2 = generator.next_id()
    id3 = generator.next_id()
    
    assert id1 < id2
    assert id2 < id3

def test_multi_threaded_concurrency():
    generator = SnowflakeIdGenerator(1, 1, CUSTOM_EPOCH, 5)
    thread_count = 10
    iterations = 1000
    generated_ids = set()
    lock = threading.Lock()

    def generate():
        local_ids = []
        for _ in range(iterations):
            local_ids.append(generator.next_id())
        with lock:
            for i in local_ids:
                generated_ids.add(i)

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        for _ in range(thread_count):
            executor.submit(generate)

    assert len(generated_ids) == thread_count * iterations

def test_sequence_rollover():
    class MockGenerator(SnowflakeIdGenerator):
        def __init__(self):
            super().__init__(1, 1, CUSTOM_EPOCH, 5)
            self.current_time = CUSTOM_EPOCH + 1000

        def _time_gen(self):
            return self.current_time

        def _til_next_millis(self, last_timestamp):
            self.current_time += 1
            return self.current_time

    generator = MockGenerator()
    
    for _ in range(4096):
        generator.next_id()
        
    next_id = generator.next_id()
    components = generator.parse(next_id)
    
    assert components.sequence == 0
    assert components.timestamp == CUSTOM_EPOCH + 1001

def test_clock_moved_backwards_exception():
    class MockGenerator(SnowflakeIdGenerator):
        def __init__(self):
            super().__init__(1, 1, CUSTOM_EPOCH, 5)
            self.current_time = CUSTOM_EPOCH + 1000

        def _time_gen(self):
            return self.current_time

    generator = MockGenerator()
    generator.next_id()
    
    generator.current_time -= 10
    
    with pytest.raises(ClockMovedBackwardsException):
        generator.next_id()

def test_clock_moved_backwards_spin_wait():
    class MockGenerator(SnowflakeIdGenerator):
        def __init__(self):
            super().__init__(1, 1, CUSTOM_EPOCH, 5)
            self.current_time = CUSTOM_EPOCH + 1000

        def _time_gen(self):
            return self.current_time

        def _til_next_millis(self, last_timestamp):
            self.current_time = last_timestamp + 1
            return self.current_time

    generator = MockGenerator()
    generator.next_id()
    
    generator.current_time -= 3
    
    next_id = generator.next_id()
    components = generator.parse(next_id)
    
    assert components.timestamp > CUSTOM_EPOCH + 1000
