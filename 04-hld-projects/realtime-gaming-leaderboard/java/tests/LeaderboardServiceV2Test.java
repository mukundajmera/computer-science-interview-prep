import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class LeaderboardServiceV2Test {

    // ------------------------------------------------------------------
    // v1 parity tests: same scenarios as LeaderboardServiceTest, run
    // against v2.
    // ------------------------------------------------------------------

    @Test
    public void testScoreUpdateAndAccurateRanking() {
        LeaderboardServiceV2 service = new LeaderboardServiceV2(100);
        service.incrementScore("user1", 50, 1000);
        service.incrementScore("user2", 30, 1001);

        assertEquals(50, service.getScore("user1"));
        assertEquals(1, service.getRank("user1"));
        assertEquals(2, service.getRank("user2"));

        service.incrementScore("user2", 30, 1002);
        assertEquals(60, service.getScore("user2"));
        assertEquals(1, service.getRank("user2"));
        assertEquals(2, service.getRank("user1"));
    }

    @Test
    public void testTopKLeaderboardOrdering() {
        LeaderboardServiceV2 service = new LeaderboardServiceV2(100);
        for (int i = 1; i <= 15; i++) {
            service.incrementScore("user" + i, i * 10, 1000 + i);
        }

        List<SkipListSortedSetV2.Entry> top10 = service.getTopK(10);
        assertEquals(10, top10.size());
        assertEquals("user15", top10.get(0).userId);
        assertEquals(150, top10.get(0).score);
        assertEquals("user14", top10.get(1).userId);
        assertEquals("user6", top10.get(9).userId);
        assertEquals(60, top10.get(9).score);
    }

    @Test
    public void testRelativeNeighborRankWindow() {
        LeaderboardServiceV2 service = new LeaderboardServiceV2(100);
        for (int i = 1; i <= 10; i++) {
            service.incrementScore("user" + i, i * 10, 1000 + i);
        }

        assertEquals(3, service.getRank("user8"));

        List<SkipListSortedSetV2.Entry> window = service.getRelativeWindow("user8", 2);
        assertEquals(5, window.size());
        assertEquals("user10", window.get(0).userId);
        assertEquals("user9", window.get(1).userId);
        assertEquals("user8", window.get(2).userId);
        assertEquals("user7", window.get(3).userId);
        assertEquals("user6", window.get(4).userId);

        List<SkipListSortedSetV2.Entry> window2 = service.getRelativeWindow("user1", 2);
        assertEquals(3, window2.size());
        assertEquals("user3", window2.get(0).userId);
        assertEquals("user1", window2.get(2).userId);
    }

    @Test
    public void testTieBreakingPrecedence() {
        LeaderboardServiceV2 service = new LeaderboardServiceV2(100);
        service.incrementScore("u1", 100, 1005);  // middle
        service.incrementScore("u2", 100, 1000);  // earliest
        service.incrementScore("u3", 100, 1010);  // latest

        assertEquals(1, service.getRank("u2"));
        assertEquals(2, service.getRank("u1"));
        assertEquals(3, service.getRank("u3"));

        List<SkipListSortedSetV2.Entry> top3 = service.getTopK(3);
        assertEquals("u2", top3.get(0).userId);
        assertEquals("u1", top3.get(1).userId);
        assertEquals("u3", top3.get(2).userId);
    }

    @Test
    public void testScoreRangePartitionRouting() {
        LeaderboardServiceV2 service = new LeaderboardServiceV2(100);
        service.incrementScore("u1", 50, 1);    // part 0
        service.incrementScore("u2", 150, 2);   // part 100
        service.incrementScore("u3", 250, 3);   // part 200

        assertEquals(1, service.getRank("u3"));
        assertEquals(2, service.getRank("u2"));
        assertEquals(3, service.getRank("u1"));

        service.incrementScore("u1", 300, 4);
        assertEquals(1, service.getRank("u1"));
        assertEquals(2, service.getRank("u3"));
        assertEquals(3, service.getRank("u2"));
        assertEquals(350, service.getScore("u1"));
    }

    // ------------------------------------------------------------------
    // v2-only tests: one or more per improvement.
    // ------------------------------------------------------------------

    // Improvement #1: cheat-resistant score validation (FOLLOW-UPS.md #3).

    @Test
    public void testMaxIncrementRejectsCheat() {
        LeaderboardServiceV2 service = new LeaderboardServiceV2(100, 1000, 1);
        assertTrue(service.incrementScore("user1", 500, 1000));

        // A bot injecting a huge raw score is rejected.
        assertFalse(service.incrementScore("user1", 9_999_999, 1001));

        assertEquals(500, service.getScore("user1"), "rejected increment never applies");
        assertEquals(1, service.getSuspiciousRejected());
        assertEquals(1, service.getRank("user1"));
    }

    @Test
    public void testRejectedUpdateNeverLogged() {
        LeaderboardServiceV2 service = new LeaderboardServiceV2(100, 1000, 1);
        service.incrementScore("user1", 100, 1000);
        service.incrementScore("user1", 50_000, 1001);

        List<LeaderboardServiceV2.ScoreEvent> log = service.getEventLog();
        assertEquals(1, log.size(), "only accepted updates reach the durable log");
        assertEquals("user1", log.get(0).userId);
        assertEquals(100, log.get(0).scoreIncrement);
    }

    @Test
    public void testValidationDisabledByDefaultParity() {
        LeaderboardServiceV2 service = new LeaderboardServiceV2(100);
        assertTrue(service.incrementScore("user1", 9_999_999, 1000));
        assertEquals(9_999_999, service.getScore("user1"));
    }

    // Improvement #2: durable event log with replay rebuild
    // (FOLLOW-UPS.md #4).

    @Test
    public void testEventLogRecordsAllAcceptedUpdates() {
        LeaderboardServiceV2 service = new LeaderboardServiceV2(100);
        service.incrementScore("u1", 50, 1000);
        service.incrementScore("u2", 70, 1001);
        service.incrementScore("u1", 30, 1002);

        List<LeaderboardServiceV2.ScoreEvent> log = service.getEventLog();
        assertEquals(3, log.size());
        assertEquals("u1", log.get(0).userId);
        assertEquals(50, log.get(0).scoreIncrement);
        assertEquals("u2", log.get(1).userId);
        assertEquals("u1", log.get(2).userId);
        assertEquals(30, log.get(2).scoreIncrement);
    }

    @Test
    public void testReplayRebuildsIdenticalState() {
        LeaderboardServiceV2 service = new LeaderboardServiceV2(100);
        for (int i = 1; i <= 10; i++) {
            service.incrementScore("user" + i, i * 10, 1000 + i);
        }

        // Fresh primary rebuilt from the durable log after a failover.
        LeaderboardServiceV2 rebuilt = new LeaderboardServiceV2(100);
        rebuilt.replayLog(service.getEventLog());

        List<SkipListSortedSetV2.Entry> originalTop = service.getTopK(10);
        List<SkipListSortedSetV2.Entry> rebuiltTop = rebuilt.getTopK(10);
        assertEquals(originalTop.size(), rebuiltTop.size());
        for (int i = 0; i < originalTop.size(); i++) {
            assertEquals(originalTop.get(i).userId, rebuiltTop.get(i).userId);
        }
        for (int i = 1; i <= 10; i++) {
            assertEquals(service.getRank("user" + i), rebuilt.getRank("user" + i));
            assertEquals(service.getScore("user" + i), rebuilt.getScore("user" + i));
        }
    }

    @Test
    public void testReplayIntoCorruptedServiceRecovers() {
        LeaderboardServiceV2 service = new LeaderboardServiceV2(100);
        service.incrementScore("u1", 100, 1000);
        service.incrementScore("u2", 200, 1001);
        List<LeaderboardServiceV2.ScoreEvent> log = service.getEventLog();

        // Simulate catastrophic in-memory loss, then reconcile from the log.
        service.replayLog(log);
        assertEquals(1, service.getRank("u2"));
        assertEquals(2, service.getRank("u1"));
        assertEquals(100, service.getScore("u1"));
    }

    // Improvement #3: hot-shard hash subdivision (FOLLOW-UPS.md #5).

    @Test
    public void testSubdivisionPreservesGlobalOrder() {
        LeaderboardServiceV2 plain = new LeaderboardServiceV2(100);
        LeaderboardServiceV2 subdivided = new LeaderboardServiceV2(100, null, 4);

        for (int i = 1; i <= 20; i++) {
            plain.incrementScore("u" + i, i * 5, 1000 + i);
            subdivided.incrementScore("u" + i, i * 5, 1000 + i);
        }
        plain.incrementScore("u1", 500, 2000);
        subdivided.incrementScore("u1", 500, 2000);

        List<SkipListSortedSetV2.Entry> plainTop = plain.getTopK(20);
        List<SkipListSortedSetV2.Entry> subTop = subdivided.getTopK(20);
        assertEquals(plainTop.size(), subTop.size());
        for (int i = 0; i < plainTop.size(); i++) {
            assertEquals(plainTop.get(i).userId, subTop.get(i).userId);
        }
        for (int i = 1; i <= 20; i++) {
            assertEquals(plain.getRank("u" + i), subdivided.getRank("u" + i));
        }
    }

    @Test
    public void testSubdivisionRelativeWindowMatchesPlain() {
        LeaderboardServiceV2 plain = new LeaderboardServiceV2(100);
        LeaderboardServiceV2 subdivided = new LeaderboardServiceV2(100, null, 3);

        for (int i = 1; i <= 12; i++) {
            plain.incrementScore("p" + i, i * 7, 1000 + i);
            subdivided.incrementScore("p" + i, i * 7, 1000 + i);
        }

        List<SkipListSortedSetV2.Entry> plainWindow = plain.getRelativeWindow("p6", 2);
        List<SkipListSortedSetV2.Entry> subWindow = subdivided.getRelativeWindow("p6", 2);
        assertEquals(plainWindow.size(), subWindow.size());
        for (int i = 0; i < plainWindow.size(); i++) {
            assertEquals(plainWindow.get(i).userId, subWindow.get(i).userId);
        }
    }
}
