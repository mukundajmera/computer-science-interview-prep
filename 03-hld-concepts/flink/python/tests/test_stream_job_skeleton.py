import os
import sys
import pytest
from datetime import datetime

# Add the v1-simple directory to the sys path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from stream_job_skeleton import StreamJobSkeleton, JobConfig


class ListSource:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def read_next(self):
        if self.index < len(self.data):
            val = self.data[self.index]
            self.index += 1
            return val
        return None

class PrefixOperator:
    def __init__(self, prefix):
        self.prefix = prefix

    def process(self, input_record, event_time):
        return f"{self.prefix}{input_record}"

class ListSink:
    def __init__(self):
        self.results = []

    def write(self, record):
        self.results.append(record)


def test_job_config_creation():
    config = JobConfig(job_name="TestJob", checkpoint_interval_ms=1000, allowed_lateness_ms=500)
    assert config.job_name == "TestJob"
    assert config.checkpoint_interval_ms == 1000
    assert config.allowed_lateness_ms == 500


def test_stream_job_processing():
    job = StreamJobSkeleton()
    
    source = ListSource([42])
    operator = PrefixOperator("Processed: ")
    sink = ListSink()
    
    job.run(source, operator, sink)
    
    assert len(sink.results) == 1
    assert sink.results[0] == "Processed: 42"

def test_stream_job_empty_source():
    job = StreamJobSkeleton()
    
    source = ListSource([])
    operator = PrefixOperator("Processed: ")
    sink = ListSink()
    
    job.run(source, operator, sink)
    
    assert len(sink.results) == 0

def test_stream_job_multiple_elements():
    # The current run implementation only processes ONE element and returns
    # But for a real stream job it might loop.
    # Given the implementation just calls source.read_next() once:
    job = StreamJobSkeleton()
    
    source = ListSource([1, 2, 3])
    operator = PrefixOperator("V")
    sink = ListSink()
    
    # Run once
    job.run(source, operator, sink)
    assert sink.results == ["V1"]
    
    # Run twice
    job.run(source, operator, sink)
    assert sink.results == ["V1", "V2"]
