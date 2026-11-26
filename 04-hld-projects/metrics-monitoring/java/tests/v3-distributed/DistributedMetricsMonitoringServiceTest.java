package v3;

import org.junit.jupiter.api.Test;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedMetricsMonitoringServiceTest {

    @Test
    public void testConsistentHashRing() {
        DistributedMetricsMonitoringService.ConsistentHashRing ring =
            new DistributedMetricsMonitoringService.ConsistentHashRing(10);

        ring.addNode("node1");
        ring.addNode("node2");
        ring.addNode("node3");

        List<String> nodes = ring.getNodes("test_metric", 2);
        assertEquals(2, nodes.size());
        assertEquals(2, new HashSet<>(nodes).size());

        ring.removeNode(nodes.get(0));
        List<String> newNodes = ring.getNodes("test_metric", 2);
        assertEquals(2, newNodes.size());
        assertFalse(newNodes.contains(nodes.get(0)));
    }

    @Test
    public void testIngestAndQueryScatterGather() {
        DistributedMetricsMonitoringService service = new DistributedMetricsMonitoringService(3, 2);

        Map<String, String> tags = new HashMap<>();
        tags.put("method", "GET");

        DistributedMetricsMonitoringService.MetricPoint p1 =
            new DistributedMetricsMonitoringService.MetricPoint("http_requests", DistributedMetricsMonitoringService.MetricType.COUNTER, tags, 1000, 1.0);
        DistributedMetricsMonitoringService.MetricPoint p2 =
            new DistributedMetricsMonitoringService.MetricPoint("http_requests", DistributedMetricsMonitoringService.MetricType.COUNTER, tags, 2000, 2.0);

        Map<String, String> tags2 = new HashMap<>();
        tags2.put("host", "web1");
        DistributedMetricsMonitoringService.MetricPoint p3 =
            new DistributedMetricsMonitoringService.MetricPoint("cpu_usage", DistributedMetricsMonitoringService.MetricType.GAUGE, tags2, 1500, 85.5);

        service.ingest(p1);
        service.ingest(p2);
        service.ingest(p3);

        double total = service.getCounterTotal("http_requests", tags, 0, 3000);
        assertEquals(3.0, total, 0.001);

        double gauge = service.getGaugeLatest("cpu_usage", tags2, 0, 3000);
        assertEquals(85.5, gauge, 0.001);
    }

    @Test
    public void testTieredStorageFlush() {
        DistributedMetricsMonitoringService service = new DistributedMetricsMonitoringService(1, 1);
        DistributedMetricsMonitoringService.Node node = service.getNode("node_0");

        DistributedMetricsMonitoringService.MetricPoint p1 =
            new DistributedMetricsMonitoringService.MetricPoint("test", DistributedMetricsMonitoringService.MetricType.COUNTER, new HashMap<>(), 1000, 5.0);

        service.ingest(p1);

        service.flushAll(); // WAL to Chunks
        service.coldFlushAll(0); // Chunks to Cold Store

        double total = service.getCounterTotal("test", new HashMap<>(), 0, 2000);
        assertEquals(5.0, total, 0.001);
    }

    @Test
    public void testNodeFailoverAndReconciliation() {
        DistributedMetricsMonitoringService service = new DistributedMetricsMonitoringService(3, 2);

        DistributedMetricsMonitoringService.MetricPoint p1 =
            new DistributedMetricsMonitoringService.MetricPoint("reqs", DistributedMetricsMonitoringService.MetricType.COUNTER, new HashMap<>(), 1000, 10.0);

        String shardKey = service.getShardKey("reqs", new HashMap<>());
        List<String> targetNodes = service.getRing().getNodes(shardKey, 2);

        String downNode = targetNodes.get(0);
        String upNode = targetNodes.get(1);

        service.setNodeStatus(downNode, false);

        service.ingest(p1);

        service.setNodeStatus(downNode, true);

        List<DistributedMetricsMonitoringService.MetricPoint> downNodePoints =
            service.getNode(downNode).query("reqs", new HashMap<>(), 0, 2000);
        assertEquals(0, downNodePoints.size());

        service.reconcileReplicas("reqs", new HashMap<>(), 0, 2000);

        downNodePoints = service.getNode(downNode).query("reqs", new HashMap<>(), 0, 2000);
        List<DistributedMetricsMonitoringService.MetricPoint> upNodePoints =
            service.getNode(upNode).query("reqs", new HashMap<>(), 0, 2000);

        assertEquals(1, downNodePoints.size());
        assertEquals(1, upNodePoints.size());
    }
}
