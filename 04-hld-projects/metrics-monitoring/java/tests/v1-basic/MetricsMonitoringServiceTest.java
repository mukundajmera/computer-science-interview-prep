package v1;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class MetricsMonitoringServiceTest {

    private MetricsMonitoringService service;

    @BeforeEach
    public void setUp() {
        service = new MetricsMonitoringService();
    }

    @Test
    public void testIngestAndQueryRange() {
        Map<String, String> tags = new HashMap<>();
        tags.put("host", "server-1");

        service.ingest(new MetricsMonitoringService.MetricPoint("cpu_usage", MetricsMonitoringService.MetricType.GAUGE, tags, 1000, 50.0));
        service.ingest(new MetricsMonitoringService.MetricPoint("cpu_usage", MetricsMonitoringService.MetricType.GAUGE, tags, 2000, 60.0));
        service.ingest(new MetricsMonitoringService.MetricPoint("cpu_usage", MetricsMonitoringService.MetricType.GAUGE, tags, 3000, 70.0));

        List<MetricsMonitoringService.MetricPoint> result = service.queryRange("cpu_usage", tags, 1500, 3500);
        assertEquals(2, result.size());
        assertEquals(60.0, result.get(0).getValue());
        assertEquals(70.0, result.get(1).getValue());
    }

    @Test
    public void testAggregations() {
        Map<String, String> tags = Collections.singletonMap("env", "prod");

        // Counter
        service.ingest(new MetricsMonitoringService.MetricPoint("requests", MetricsMonitoringService.MetricType.COUNTER, tags, 100, 10));
        service.ingest(new MetricsMonitoringService.MetricPoint("requests", MetricsMonitoringService.MetricType.COUNTER, tags, 200, 15));
        assertEquals(25.0, service.getCounterTotal("requests", tags, 0, 1000));

        // Gauge
        service.ingest(new MetricsMonitoringService.MetricPoint("memory", MetricsMonitoringService.MetricType.GAUGE, tags, 100, 1024));
        service.ingest(new MetricsMonitoringService.MetricPoint("memory", MetricsMonitoringService.MetricType.GAUGE, tags, 200, 2048));
        assertEquals(2048.0, service.getGaugeLatest("memory", tags, 0, 1000));

        // Histogram
        service.ingest(new MetricsMonitoringService.MetricPoint("latency", MetricsMonitoringService.MetricType.HISTOGRAM, tags, 100, 10.0));
        service.ingest(new MetricsMonitoringService.MetricPoint("latency", MetricsMonitoringService.MetricType.HISTOGRAM, tags, 200, 50.0));
        service.ingest(new MetricsMonitoringService.MetricPoint("latency", MetricsMonitoringService.MetricType.HISTOGRAM, tags, 300, 100.0));
        service.ingest(new MetricsMonitoringService.MetricPoint("latency", MetricsMonitoringService.MetricType.HISTOGRAM, tags, 400, 200.0));

        // P50 should be 50.0 or 100.0 depending on math.ceil(0.5 * 4) = 2 -> index 1 -> 50.0
        assertEquals(50.0, service.getHistogramPercentile("latency", tags, 0, 1000, 50.0));
        // P90 math.ceil(0.9 * 4) = 4 -> index 3 -> 200.0
        assertEquals(200.0, service.getHistogramPercentile("latency", tags, 0, 1000, 90.0));
        // P99
        assertEquals(200.0, service.getHistogramPercentile("latency", tags, 0, 1000, 99.0));
    }

    @Test
    public void testAlertFiring() {
        service.registerAlertRule(new MetricsMonitoringService.AlertRule("cpu_high", "cpu_usage", 80.0, true));

        service.ingest(new MetricsMonitoringService.MetricPoint("cpu_usage", MetricsMonitoringService.MetricType.GAUGE, null, 1000, 70.0));
        List<MetricsMonitoringService.AlertEvent> events1 = service.evaluateAlerts(1500);
        assertTrue(events1.isEmpty());

        service.ingest(new MetricsMonitoringService.MetricPoint("cpu_usage", MetricsMonitoringService.MetricType.GAUGE, null, 2000, 85.0));
        List<MetricsMonitoringService.AlertEvent> events2 = service.evaluateAlerts(2500);
        assertEquals(1, events2.size());
        assertEquals("cpu_high", events2.get(0).getRuleId());
        assertEquals(MetricsMonitoringService.AlertStatus.FIRING, events2.get(0).getStatus());
    }

    @Test
    public void testAlertResolving() {
        service.registerAlertRule(new MetricsMonitoringService.AlertRule("cpu_high", "cpu_usage", 80.0, true));

        // Fire
        service.ingest(new MetricsMonitoringService.MetricPoint("cpu_usage", MetricsMonitoringService.MetricType.GAUGE, null, 1000, 85.0));
        service.evaluateAlerts(1500);

        // Resolve
        service.ingest(new MetricsMonitoringService.MetricPoint("cpu_usage", MetricsMonitoringService.MetricType.GAUGE, null, 2000, 75.0));
        List<MetricsMonitoringService.AlertEvent> events = service.evaluateAlerts(2500);

        assertEquals(1, events.size());
        assertEquals("cpu_high", events.get(0).getRuleId());
        assertEquals(MetricsMonitoringService.AlertStatus.RESOLVED, events.get(0).getStatus());
    }
}
