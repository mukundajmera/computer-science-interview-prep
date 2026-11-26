import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

public class VideoRankingServiceTest {

    private VideoRankingService service;

    @BeforeEach
    void setUp() {
        service = new VideoRankingService();
    }

    @Test
    void testViewTracking() {
        service.recordView("v1");
        service.recordView("v1");
        service.recordView("v2");

        Assertions.assertEquals(2L, service.getViewCount("v1"));
        Assertions.assertEquals(1L, service.getViewCount("v2"));
        Assertions.assertEquals(0L, service.getViewCount("v3"));
    }

    @Test
    void testTopKRankingAccuracy() {
        service.recordView("v1");
        service.recordView("v1");
        service.recordView("v2");
        service.recordView("v3");
        service.recordView("v3");
        service.recordView("v3");

        List<VideoRank> top2 = service.getTopK(2);
        Assertions.assertEquals(2, top2.size());
        
        Assertions.assertEquals("v3", top2.get(0).getVideoId());
        Assertions.assertEquals(3L, top2.get(0).getViewCount());
        Assertions.assertEquals(1, top2.get(0).getRank());

        Assertions.assertEquals("v1", top2.get(1).getVideoId());
        Assertions.assertEquals(2L, top2.get(1).getViewCount());
        Assertions.assertEquals(2, top2.get(1).getRank());
    }

    @Test
    void testTieBreaking() {
        service.recordView("vA");
        service.recordView("vB");
        service.recordView("vC");

        List<VideoRank> top2 = service.getTopK(2);
        Assertions.assertEquals(2, top2.size());
        
        // Lexicographically smaller wins
        Assertions.assertEquals("vA", top2.get(0).getVideoId());
        Assertions.assertEquals(1L, top2.get(0).getViewCount());
        Assertions.assertEquals(1, top2.get(0).getRank());

        Assertions.assertEquals("vB", top2.get(1).getVideoId());
        Assertions.assertEquals(1L, top2.get(1).getViewCount());
        Assertions.assertEquals(2, top2.get(1).getRank());
    }

    @Test
    void testEmptyRanking() {
        List<VideoRank> top3 = service.getTopK(3);
        Assertions.assertTrue(top3.isEmpty());
    }

    @Test
    void testLargeVolumeViewIncrements() {
        for (int i = 0; i < 1000; i++) {
            service.recordView("vPopular");
        }
        for (int i = 0; i < 100; i++) {
            service.recordView("vMid");
        }

        Assertions.assertEquals(1000L, service.getViewCount("vPopular"));
        
        List<VideoRank> top = service.getTopK(1);
        Assertions.assertEquals(1, top.size());
        Assertions.assertEquals("vPopular", top.get(0).getVideoId());
        Assertions.assertEquals(1000L, top.get(0).getViewCount());
    }

    @Test
    void testWindowReset() {
        service.recordView("v1");
        service.recordView("v2");
        Assertions.assertEquals(1L, service.getViewCount("v1"));

        service.resetWindow();
        Assertions.assertEquals(0L, service.getViewCount("v1"));
        Assertions.assertEquals(0L, service.getViewCount("v2"));
        Assertions.assertTrue(service.getTopK(5).isEmpty());
    }
}
