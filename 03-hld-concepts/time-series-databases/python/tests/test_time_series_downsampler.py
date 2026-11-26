import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from time_series_downsampler import TimeSeriesDownsampler, DataPoint, AggregationType

def test_insert_and_range_query():
    tsdb = TimeSeriesDownsampler()
    tsdb.insert(DataPoint("cpu_usage", 1000, 45.0, {"host": "server1"}))
    tsdb.insert(DataPoint("cpu_usage", 2000, 50.0, {"host": "server1"}))
    tsdb.insert(DataPoint("cpu_usage", 3000, 55.0, {"host": "server2"}))

    # Range query without tags
    results = tsdb.range_query("cpu_usage", 1000, 2500)
    assert len(results) == 2
    assert results[0].value == 45.0
    assert results[1].value == 50.0

    # Range query with tags
    results_with_tags = tsdb.range_query("cpu_usage", 1000, 3000, {"host": "server2"})
    assert len(results_with_tags) == 1
    assert results_with_tags[0].value == 55.0

def test_downsample_avg():
    tsdb = TimeSeriesDownsampler()
    # 60s bucket
    tsdb.insert(DataPoint("memory_usage", 60, 10.0))
    tsdb.insert(DataPoint("memory_usage", 90, 20.0)) # Same bucket as 60: 60..119
    tsdb.insert(DataPoint("memory_usage", 120, 30.0))
    tsdb.insert(DataPoint("memory_usage", 150, 40.0))

    results = tsdb.downsample("memory_usage", 60, AggregationType.AVG)

    assert len(results) == 2
    assert results[0].timestamp == 60
    assert results[0].value == 15.0 # (10+20)/2
    assert results[1].timestamp == 120
    assert results[1].value == 35.0 # (30+40)/2

def test_downsample_min_max_sum():
    tsdb = TimeSeriesDownsampler()
    tsdb.insert(DataPoint("requests", 10, 5.0))
    tsdb.insert(DataPoint("requests", 20, 10.0))
    tsdb.insert(DataPoint("requests", 30, 2.0))
    tsdb.insert(DataPoint("requests", 40, 8.0))

    # 100s bucket size, so all these fall in bucket 0
    results_min = tsdb.downsample("requests", 100, AggregationType.MIN)
    assert len(results_min) == 1
    assert results_min[0].value == 2.0

    results_max = tsdb.downsample("requests", 100, AggregationType.MAX)
    assert len(results_max) == 1
    assert results_max[0].value == 10.0

    results_sum = tsdb.downsample("requests", 100, AggregationType.SUM)
    assert len(results_sum) == 1
    assert results_sum[0].value == 25.0

def test_apply_retention():
    tsdb = TimeSeriesDownsampler()
    tsdb.insert(DataPoint("temp", 1000, 20.0))
    tsdb.insert(DataPoint("temp", 2000, 22.0))
    tsdb.insert(DataPoint("temp", 3000, 21.0))

    # Current time is 3500, retention period is 1000s
    # Cutoff time will be 2500. Points at 1000 and 2000 should be removed.
    tsdb.apply_retention(3500, 1000)

    results = tsdb.range_query("temp", 0, 5000)
    assert len(results) == 1
    assert results[0].timestamp == 3000
    assert results[0].value == 21.0
