import v1_basic.CdnSimulator;
import java.util.ArrayList;
import java.util.List;

public class CdnSimulatorTest {

    public static void main(String[] args) {
        testNormalHit();
        testThunderingHerdCoalescing();
        System.out.println("All tests passed.");
    }

    private static void testNormalHit() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/images/logo.png", "binary_data_123");

        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);
        CdnSimulator.EdgeNode edge = new CdnSimulator.EdgeNode(shield);

        // Miss -> hits origin
        String result1 = edge.fetch("/images/logo.png");
        assert "binary_data_123".equals(result1) : "Expected binary_data_123";
        assert origin.fetchCount == 1 : "Expected 1 origin fetch";

        // Hit -> hits edge cache
        String result2 = edge.fetch("/images/logo.png");
        assert "binary_data_123".equals(result2) : "Expected binary_data_123";
        assert edge.cacheHitCount == 1 : "Expected 1 edge cache hit";
        assert origin.fetchCount == 1 : "Origin should not be hit again";
    }

    private static void testThunderingHerdCoalescing() {
        CdnSimulator.CustomerOrigin origin = new CdnSimulator.CustomerOrigin();
        origin.put("/videos/viral.mp4", "video_data_999");

        CdnSimulator.OriginShield shield = new CdnSimulator.OriginShield(origin);
        CdnSimulator.EdgeNode edge = new CdnSimulator.EdgeNode(shield);

        List<String> results = new ArrayList<>();
        // Simulate 10,000 concurrent requests hitting the edge and then the shield
        // because of a sudden cache miss/purge
        edge.fetchBatch("/videos/viral.mp4", 10000, results);

        assert results.size() == 10000 : "Expected 10000 results";
        for (String res : results) {
            assert "video_data_999".equals(res) : "Expected video_data_999";
        }

        // Thundering herd invariant: Origin is protected by request coalescing
        // 10,000 requests to the shield should result in exactly 1 request to the Origin
        assert origin.fetchCount == 1 : "Expected exactly 1 origin fetch, but got " + origin.fetchCount;
        assert shield.fetchCount == 10000 : "Shield should receive all 10000 requests";
    }
}
