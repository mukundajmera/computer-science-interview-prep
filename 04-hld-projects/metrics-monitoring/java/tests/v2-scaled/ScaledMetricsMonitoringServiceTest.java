package v2_scaled;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class ScaledMetricsMonitoringServiceTest {

    private ScaledMetricsMonitoringService service;

    @Test
    public void testHighThroughputIngestionAndFlush() {
        service = new ScaledMetricsMonitoringService(3);
        Map<String, String> tags = Collections.singletonMap("host", "server-1");

        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("cpu_usage", ScaledMetricsMonitoringService.MetricType.GAUGE, tags, 1000, 50.0));
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("cpu_usage", ScaledMetricsMonitoringService.MetricType.GAUGE, tags, 2000, 60.0));

        // Should not be flushed yet
        assertEquals(0, service.getRawData().size());
        assertEquals(2, service.getIngestionBuffer().size());

        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("cpu_usage", ScaledMetricsMonitoringService.MetricType.GAUGE, tags, 3000, 70.0));

        // Batch size of 3 reached, should be flushed
        assertEquals(3, service.getRawData().size());
        assertEquals(0, service.getIngestionBuffer().size());

        @SuppressWarnings("unchecked")
        List<ScaledMetricsMonitoringService.MetricPoint> result = (List<ScaledMetricsMonitoringService.MetricPoint>) service.queryRange("cpu_usage", tags, 1500, 3500, ScaledMetricsMonitoringService.Resolution.RAW);
        assertEquals(2, result.size());
        assertEquals(60.0, result.get(0).getValue());
        assertEquals(70.0, result.get(1).getValue());
    }

    @Test
    public void testMultiResolutionDownsampling() {
        service = new ScaledMetricsMonitoringService(1);
        Map<String, String> tags = Collections.singletonMap("env", "prod");

        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("requests", ScaledMetricsMonitoringService.MetricType.COUNTER, tags, 1000, 10));
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("requests", ScaledMetricsMonitoringService.MetricType.COUNTER, tags, 2000, 20));
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("requests", ScaledMetricsMonitoringService.MetricType.COUNTER, tags, 3000, 30));

        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("requests", ScaledMetricsMonitoringService.MetricType.COUNTER, tags, 65000, 40));
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("requests", ScaledMetricsMonitoringService.MetricType.COUNTER, tags, 3605000, 100));

        @SuppressWarnings("unchecked")
        List<ScaledMetricsMonitoringService.RollupPoint> rollups1m = (List<ScaledMetricsMonitoringService.RollupPoint>) service.queryRange("requests", tags, 0, 4000000, ScaledMetricsMonitoringService.Resolution.ONE_MIN);
        assertEquals(3, rollups1m.size());

        assertEquals(0, rollups1m.get(0).getWindowStartMs());
        assertEquals(3, rollups1m.get(0).getCount());
        assertEquals(60.0, rollups1m.get(0).getSumValue());
        assertEquals(10.0, rollups1m.get(0).getMinValue());
        assertEquals(30.0, rollups1m.get(0).getMaxValue());

        @SuppressWarnings("unchecked")
        List<ScaledMetricsMonitoringService.RollupPoint> rollups1h = (List<ScaledMetricsMonitoringService.RollupPoint>) service.queryRange("requests", tags, 0, 4000000, ScaledMetricsMonitoringService.Resolution.ONE_HOUR);
        assertEquals(2, rollups1h.size());

        assertEquals(0, rollups1h.get(0).getWindowStartMs());
        assertEquals(4, rollups1h.get(0).getCount());
        assertEquals(100.0, rollups1h.get(0).getSumValue());
    }

    @Test
    public void testSlidingWindowPercentiles() {
        service = new ScaledMetricsMonitoringService(1);
        Map<String, String> tags = Collections.singletonMap("service", "api");

        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("latency", ScaledMetricsMonitoringService.MetricType.HISTOGRAM, tags, 100, 10.0));
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("latency", ScaledMetricsMonitoringService.MetricType.HISTOGRAM, tags, 200, 50.0));
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("latency", ScaledMetricsMonitoringService.MetricType.HISTOGRAM, tags, 300, 100.0));
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("latency", ScaledMetricsMonitoringService.MetricType.HISTOGRAM, tags, 400, 200.0));
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("latency", ScaledMetricsMonitoringService.MetricType.HISTOGRAM, tags, 500, 500.0));

        assertEquals(100.0, service.getSlidingWindowPercentile("latency", tags, 0, 1000, 50.0));
        assertEquals(500.0, service.getSlidingWindowPercentile("latency", tags, 0, 1000, 90.0));
        assertEquals(500.0, service.getSlidingWindowPercentile("latency", tags, 0, 1000, 99.0));
    }

    @Test
    public void testAlertThresholdHysteresisAndCooldown() {
        service = new ScaledMetricsMonitoringService(1);
        service.registerAlertRule(new ScaledMetricsMonitoringService.AlertRule("cpu_high", "cpu_usage", 80.0, true, 10.0, 5000));

        // Fire
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("cpu_usage", ScaledMetricsMonitoringService.MetricType.GAUGE, null, 1000, 85.0));
        List<ScaledMetricsMonitoringService.AlertEvent> events = service.evaluateAlerts(1500);
        assertEquals(1, events.size());
        assertEquals("cpu_high", events.get(0).getRuleId());
        assertEquals(ScaledMetricsMonitoringService.AlertStatus.FIRING, events.get(0).getStatus());

        // Attempt to resolve within hysteresis zone (e.g. 75), should NOT resolve
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("cpu_usage", ScaledMetricsMonitoringService.MetricType.GAUGE, null, 2000, 75.0));
        events = service.evaluateAlerts(6500); // Past cooldown
        assertEquals(0, events.size());
        assertEquals(ScaledMetricsMonitoringService.AlertStatus.FIRING, service.getAlertStatus("cpu_high"));

        // Attempt to resolve below hysteresis zone (e.g. 65), but within cooldown
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("cpu_usage", ScaledMetricsMonitoringService.MetricType.GAUGE, null, 3000, 65.0));
        events = service.evaluateAlerts(3500); // Not past cooldown
        assertEquals(0, events.size());
        assertEquals(ScaledMetricsMonitoringService.AlertStatus.FIRING, service.getAlertStatus("cpu_high"));

        // Resolve past cooldown
        service.ingest(new ScaledMetricsMonitoringService.MetricPoint("cpu_usage", ScaledMetricsMonitoringService.MetricType.GAUGE, null, 4000, 65.0));
        events = service.evaluateAlerts(7000); // Past cooldown
        assertEquals(1, events.size());
        assertEquals("cpu_high", events.get(0).getRuleId());
        assertEquals(ScaledMetricsMonitoringService.AlertStatus.RESOLVED, events.get(0).getStatus());
    }
}
