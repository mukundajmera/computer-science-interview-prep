import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class LeaderboardServiceTest {

    private LeaderboardService service;

    @BeforeEach
    public void setUp() {
        service = new LeaderboardService(100);
    }

    @Test
    public void testScoreUpdateAndAccurateRanking() {
        service.incrementScore("user1", 50, 1000L);
        service.incrementScore("user2", 30, 1001L);
        
        assertEquals(50, service.getScore("user1"));
        assertEquals(1, service.getRank("user1"));
        assertEquals(2, service.getRank("user2"));
        
        service.incrementScore("user2", 30, 1002L); // score becomes 60
        
        assertEquals(60, service.getScore("user2"));
        assertEquals(1, service.getRank("user2"));
        assertEquals(2, service.getRank("user1"));
    }

    @Test
    public void testTopKLeaderboardOrdering() {
        for (int i = 1; i <= 15; i++) {
            service.incrementScore("user" + i, i * 10, 1000L + i);
        }
        
        List<SkipListSortedSet.Entry> top5 = service.getTopK(5);
        assertEquals(5, top5.size());
        
        // top scores should be 150, 140, 130, 120, 110
        assertEquals("user15", top5.get(0).userId);
        assertEquals(150, top5.get(0).score);
        assertEquals("user14", top5.get(1).userId);
        assertEquals(140, top5.get(1).score);
        assertEquals("user11", top5.get(4).userId);
    }

    @Test
    public void testRelativeNeighborRankWindow() {
        for (int i = 1; i <= 10; i++) {
            service.incrementScore("user" + i, i * 10, 1000L + i);
        }
        
        // ranks:
        // 1: user10 (100)
        // 2: user9 (90)
        // 3: user8 (80)
        // ...
        // 10: user1 (10)
        
        // user8 is rank 3
        assertEquals(3, service.getRank("user8"));
        
        // radius 2: should get ranks 1 to 5 (user10 to user6)
        List<SkipListSortedSet.Entry> window = service.getRelativeWindow("user8", 2);
        
        assertEquals(5, window.size());
        assertEquals("user10", window.get(0).userId);
        assertEquals("user9", window.get(1).userId);
        assertEquals("user8", window.get(2).userId);
        assertEquals("user7", window.get(3).userId);
        assertEquals("user6", window.get(4).userId);
        
        // boundary test (user1 is rank 10)
        List<SkipListSortedSet.Entry> windowBoundary = service.getRelativeWindow("user1", 2);
        assertEquals(3, windowBoundary.size()); // rank 8, 9, 10 -> user3, user2, user1
        assertEquals("user3", windowBoundary.get(0).userId);
        assertEquals("user1", windowBoundary.get(2).userId);
    }

    @Test
    public void testTieBreakingPrecedence() {
        // Same score, different timestamps
        service.incrementScore("user1", 100, 1005L); // Later
        service.incrementScore("user2", 100, 1000L); // Earlier, should be rank 1
        service.incrementScore("user3", 100, 1010L); // Latest
        
        assertEquals(1, service.getRank("user2"));
        assertEquals(2, service.getRank("user1"));
        assertEquals(3, service.getRank("user3"));
        
        List<SkipListSortedSet.Entry> top3 = service.getTopK(3);
        assertEquals("user2", top3.get(0).userId);
        assertEquals("user1", top3.get(1).userId);
        assertEquals("user3", top3.get(2).userId);
    }

    @Test
    public void testScoreRangePartitionRouting() {
        // Partition size is 100.
        // user1 goes to partition 0
        service.incrementScore("user1", 50, 1000L);
        // user2 goes to partition 100
        service.incrementScore("user2", 150, 1000L);
        // user3 goes to partition 200
        service.incrementScore("user3", 250, 1000L);
        
        assertEquals(1, service.getRank("user3"));
        assertEquals(2, service.getRank("user2"));
        assertEquals(3, service.getRank("user1"));
        
        // Update user1 to partition 300
        service.incrementScore("user1", 300, 1001L); // total 350
        
        assertEquals(1, service.getRank("user1"));
        assertEquals(2, service.getRank("user3"));
        assertEquals(3, service.getRank("user2"));
    }
}
