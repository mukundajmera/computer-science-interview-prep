import sys
import os
import pytest
import time

# Add the appropriate directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from simple_metrics import SimpleMetrics

def test_record_and_get_sum():
    metrics = SimpleMetrics()
    metrics.record("request_latency", 10.5)
    metrics.record("request_latency", 20.0)
    
    assert abs(metrics.get_sum("request_latency") - 30.5) < 0.001
    assert abs(metrics.get_sum("non_existent_metric") - 0.0) < 0.001

def test_increment_and_count():
    metrics = SimpleMetrics()
    metrics.increment("request_count")
    metrics.increment("request_count")
    metrics.increment("request_count")
    
    assert abs(metrics.get_sum("request_count") - 3.0) < 0.001
    assert abs(metrics.get_average("request_count") - 1.0) < 0.001

def test_get_average():
    metrics = SimpleMetrics()
    metrics.record("cpu_usage", 50.0)
    metrics.record("cpu_usage", 70.0)
    metrics.record("cpu_usage", 90.0)
    
    assert abs(metrics.get_average("cpu_usage") - 70.0) < 0.001
    assert abs(metrics.get_average("non_existent_metric") - 0.0) < 0.001
