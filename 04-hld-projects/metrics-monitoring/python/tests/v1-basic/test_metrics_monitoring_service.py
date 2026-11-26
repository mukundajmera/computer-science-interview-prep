import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

from metrics_monitoring_service import MetricsMonitoringService, MetricPoint, MetricType, AlertRule, AlertStatus

def test_ingest_and_query_range():
    service = MetricsMonitoringService()
    tags = {"host": "server-1"}

    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, tags, 1000, 50.0))
    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, tags, 2000, 60.0))
    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, tags, 3000, 70.0))

    result = service.query_range("cpu_usage", tags, 1500, 3500)
    assert len(result) == 2
    assert result[0].value == 60.0
    assert result[1].value == 70.0

def test_aggregations():
    service = MetricsMonitoringService()
    tags = {"env": "prod"}

    # Counter
    service.ingest(MetricPoint("requests", MetricType.COUNTER, tags, 100, 10))
    service.ingest(MetricPoint("requests", MetricType.COUNTER, tags, 200, 15))
    assert service.get_counter_total("requests", tags, 0, 1000) == 25.0

    # Gauge
    service.ingest(MetricPoint("memory", MetricType.GAUGE, tags, 100, 1024))
    service.ingest(MetricPoint("memory", MetricType.GAUGE, tags, 200, 2048))
    assert service.get_gauge_latest("memory", tags, 0, 1000) == 2048.0

    # Histogram
    service.ingest(MetricPoint("latency", MetricType.HISTOGRAM, tags, 100, 10.0))
    service.ingest(MetricPoint("latency", MetricType.HISTOGRAM, tags, 200, 50.0))
    service.ingest(MetricPoint("latency", MetricType.HISTOGRAM, tags, 300, 100.0))
    service.ingest(MetricPoint("latency", MetricType.HISTOGRAM, tags, 400, 200.0))

    assert service.get_histogram_percentile("latency", tags, 0, 1000, 50.0) == 50.0
    assert service.get_histogram_percentile("latency", tags, 0, 1000, 90.0) == 200.0
    assert service.get_histogram_percentile("latency", tags, 0, 1000, 99.0) == 200.0

def test_alert_firing():
    service = MetricsMonitoringService()
    service.register_alert_rule(AlertRule("cpu_high", "cpu_usage", 80.0, True))

    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, {}, 1000, 70.0))
    events1 = service.evaluate_alerts(1500)
    assert len(events1) == 0

    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, {}, 2000, 85.0))
    events2 = service.evaluate_alerts(2500)
    assert len(events2) == 1
    assert events2[0].rule_id == "cpu_high"
    assert events2[0].status == AlertStatus.FIRING

def test_alert_resolving():
    service = MetricsMonitoringService()
    service.register_alert_rule(AlertRule("cpu_high", "cpu_usage", 80.0, True))

    # Fire
    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, {}, 1000, 85.0))
    service.evaluate_alerts(1500)

    # Resolve
    service.ingest(MetricPoint("cpu_usage", MetricType.GAUGE, {}, 2000, 75.0))
    events = service.evaluate_alerts(2500)

    assert len(events) == 1
    assert events[0].rule_id == "cpu_high"
    assert events[0].status == AlertStatus.RESOLVED
