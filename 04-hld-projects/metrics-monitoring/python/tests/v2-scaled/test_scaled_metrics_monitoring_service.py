import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))

from scaled_metrics_monitoring_service import ScaledMetricsMonitoringService, MetricPoint, MetricType, AlertRule, AlertStatus, Resolution

def test_high_throughput_ingestion_and_flush():
    service = ScaledMetricsMonitoringService(batch_size=3)
    tags = {"host": "server-1"}

    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, tags, 1000, 50.0))
    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, tags, 2000, 60.0))

    # Should not be flushed yet
    assert len(service.raw_data) == 0
    assert len(service.ingestion_buffer) == 2

    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, tags, 3000, 70.0))

    # Batch size of 3 reached, should be flushed
    assert len(service.raw_data) == 3
    assert len(service.ingestion_buffer) == 0

    result = service.query_range("cpu_usage", tags, 1500, 3500)
    assert len(result) == 2
    assert result[0].value == 60.0
    assert result[1].value == 70.0

def test_multi_resolution_downsampling():
    service = ScaledMetricsMonitoringService(batch_size=1)
    tags = {"env": "prod"}

    # Ingest 3 points in same 1-min window (1000 ms, 2000 ms, 3000 ms are all in window 0)
    service.ingest(MetricPoint("requests", MetricType.COUNTER, tags, 1000, 10))
    service.ingest(MetricPoint("requests", MetricType.COUNTER, tags, 2000, 20))
    service.ingest(MetricPoint("requests", MetricType.COUNTER, tags, 3000, 30))

    # Ingest point in next 1-min window (65000 ms is in window 60000)
    service.ingest(MetricPoint("requests", MetricType.COUNTER, tags, 65000, 40))

    # Ingest point in another 1-hour window (3605000 ms is in window 3600000)
    service.ingest(MetricPoint("requests", MetricType.COUNTER, tags, 3605000, 100))

    # Query 1m rollups
    rollups_1m = service.query_range("requests", tags, 0, 4000000, Resolution.ONE_MIN)
    assert len(rollups_1m) == 3

    # First window (0)
    assert rollups_1m[0].window_start_ms == 0
    assert rollups_1m[0].count == 3
    assert rollups_1m[0].sum_value == 60.0
    assert rollups_1m[0].min_value == 10.0
    assert rollups_1m[0].max_value == 30.0

    # Query 1h rollups
    rollups_1h = service.query_range("requests", tags, 0, 4000000, Resolution.ONE_HOUR)
    assert len(rollups_1h) == 2

    # First 1h window (0)
    assert rollups_1h[0].window_start_ms == 0
    assert rollups_1h[0].count == 4
    assert rollups_1h[0].sum_value == 100.0

def test_sliding_window_percentiles():
    service = ScaledMetricsMonitoringService(batch_size=1)
    tags = {"service": "api"}

    service.ingest(MetricPoint("latency", MetricType.HISTOGRAM, tags, 100, 10.0))
    service.ingest(MetricPoint("latency", MetricType.HISTOGRAM, tags, 200, 50.0))
    service.ingest(MetricPoint("latency", MetricType.HISTOGRAM, tags, 300, 100.0))
    service.ingest(MetricPoint("latency", MetricType.HISTOGRAM, tags, 400, 200.0))
    service.ingest(MetricPoint("latency", MetricType.HISTOGRAM, tags, 500, 500.0))

    assert service.get_sliding_window_percentile("latency", tags, 0, 1000, 50.0) == 100.0
    assert service.get_sliding_window_percentile("latency", tags, 0, 1000, 90.0) == 500.0
    assert service.get_sliding_window_percentile("latency", tags, 0, 1000, 99.0) == 500.0

def test_alert_threshold_hysteresis_and_cooldown():
    service = ScaledMetricsMonitoringService(batch_size=1)
    # rule: fire if > 80, resolve if < 70 (80 - 10 hysteresis)
    # cooldown: 5000 ms
    service.register_alert_rule(AlertRule("cpu_high", "cpu_usage", threshold=80.0, greater_than=True, hysteresis=10.0, cooldown_ms=5000))

    # Fire
    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, {}, 1000, 85.0))
    events = service.evaluate_alerts(1500)
    assert len(events) == 1
    assert events[0].rule_id == "cpu_high"
    assert events[0].status == AlertStatus.FIRING

    # Attempt to resolve within hysteresis zone (e.g. 75), should NOT resolve
    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, {}, 2000, 75.0))
    events = service.evaluate_alerts(6500) # Past cooldown
    assert len(events) == 0
    assert service.current_alert_states["cpu_high"] == AlertStatus.FIRING

    # Attempt to resolve below hysteresis zone (e.g. 65), but within cooldown
    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, {}, 3000, 65.0))
    events = service.evaluate_alerts(3500) # Not past cooldown since last fire/resolve
    assert len(events) == 0
    assert service.current_alert_states["cpu_high"] == AlertStatus.FIRING

    # Resolve past cooldown
    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, {}, 4000, 65.0))
    events = service.evaluate_alerts(7000) # Past cooldown (7000 - 1500 = 5500 > 5000)
    assert len(events) == 1
    assert events[0].rule_id == "cpu_high"
    assert events[0].status == AlertStatus.RESOLVED
