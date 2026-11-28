package v2_extended;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class SocialGraphEngineTaoV2Test {

    private SocialGraphEngineTao.Database db;
    private SocialGraphEngineTao.LeaderCache leader;
    private SocialGraphEngineTao.FollowerCache follower;
    private SocialGraphEngineTao.GraphEngine engine;

    private void makeStack() {
        db = new SocialGraphEngineTao.Database();
        leader = new SocialGraphEngineTao.LeaderCache(db);
        follower = new SocialGraphEngineTao.FollowerCache(leader);
        engine = new SocialGraphEngineTao.GraphEngine(db, leader, follower);
    }

    // ---------- v1 parity: every v1 behavior still holds on the v2 track ----------

    @Test
    public void testObjectCrud() {
        SocialGraphEngineTao.Database db = new SocialGraphEngineTao.Database();
        SocialGraphEngineTao.ObjectNode obj = new SocialGraphEngineTao.ObjectNode(1, 1, "User A");
        db.addObject(obj);

        assertEquals("User A", db.getObject(1).data);
        db.updateObject(1, "User A Updated");
        assertEquals("User A Updated", db.getObject(1).data);

        db.deleteObject(1);
        assertNull(db.getObject(1));
    }

    @Test
    public void testAssociationCrudAndFollowerCache() {
        makeStack();

        long time = System.currentTimeMillis() / 1000;

        follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 2, time, ""));
        List<SocialGraphEngineTao.Association> assocs = follower.getAssociations(1, 1);
        assertEquals(1, assocs.size());
        assertEquals(2, assocs.get(0).id2);

        follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 3, time + 1, ""));
        assocs = follower.getAssociations(1, 1);
        assertEquals(2, assocs.size());

        follower.deleteAssociation(1, 1, 2);
        assocs = follower.getAssociations(1, 1);
        assertEquals(1, assocs.size());
        assertEquals(3, assocs.get(0).id2);
    }

    @Test
    public void testInvalidationBus() {
        SocialGraphEngineTao.Database db = new SocialGraphEngineTao.Database();
        SocialGraphEngineTao.LeaderCache leader = new SocialGraphEngineTao.LeaderCache(db);
        SocialGraphEngineTao.FollowerCache f1 = new SocialGraphEngineTao.FollowerCache(leader);
        SocialGraphEngineTao.FollowerCache f2 = new SocialGraphEngineTao.FollowerCache(leader);

        long time = System.currentTimeMillis() / 1000;

        f1.getAssociations(1, 1);
        assertTrue(f1.cache.containsKey("1:1"));

        f2.addAssociation(new SocialGraphEngineTao.Association(1, 1, 2, time, ""));

        assertFalse(f1.cache.containsKey("1:1"));

        List<SocialGraphEngineTao.Association> assocs = f1.getAssociations(1, 1);
        assertEquals(1, assocs.size());
        assertEquals(2, assocs.get(0).id2);
    }

    @Test
    public void testMutualFriends() {
        makeStack();

        follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 3, 1, ""));
        follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 4, 1, ""));
        follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 5, 1, ""));

        follower.addAssociation(new SocialGraphEngineTao.Association(2, 1, 4, 1, ""));
        follower.addAssociation(new SocialGraphEngineTao.Association(2, 1, 5, 1, ""));
        follower.addAssociation(new SocialGraphEngineTao.Association(2, 1, 6, 1, ""));

        List<Long> mutuals = engine.getMutualFriends(1, 2, 1);
        assertEquals(2, mutuals.size());
        assertTrue(mutuals.contains(4L));
        assertTrue(mutuals.contains(5L));
    }

    @Test
    public void testSupernodeVirtualSharding() {
        makeStack();

        long supernodeId = 1000;
        for (int i = 0; i < 20; i++) {
            follower.addAssociation(new SocialGraphEngineTao.Association(supernodeId, 1, i, i, ""));
        }

        List<SocialGraphEngineTao.Association> assocs = follower.getAssociations(supernodeId, 1);
        assertEquals(20, assocs.size());

        Set<Integer> bucketsUsed = new HashSet<>();
        for (String key : db.associations.keySet()) {
            String[] parts = key.split(":");
            if (parts.length == 3 && Long.parseLong(parts[0]) == supernodeId) {
                bucketsUsed.add(Integer.parseInt(parts[2]));
            }
        }

        assertTrue(bucketsUsed.size() > 1, "Should distribute across multiple buckets");
    }

    @Test
    public void testAssocRangeGetCount() {
        makeStack();

        long baseTime = 1000;
        follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 2, baseTime, ""));
        follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 3, baseTime + 10, ""));
        follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 4, baseTime + 20, ""));

        assertEquals(3, follower.assocCount(1, 1));

        List<SocialGraphEngineTao.Association> rangeRes = follower.assocRange(1, 1, baseTime + 5, baseTime + 25);
        assertEquals(2, rangeRes.size());
        assertTrue(rangeRes.stream().anyMatch(a -> a.id2 == 3));
        assertTrue(rangeRes.stream().anyMatch(a -> a.id2 == 4));

        Set<Long> ids = new HashSet<>();
        ids.add(2L);
        ids.add(4L);
        List<SocialGraphEngineTao.Association> getRes = follower.assocGet(1, 1, ids);
        assertEquals(2, getRes.size());
        assertTrue(getRes.stream().anyMatch(a -> a.id2 == 2));
        assertTrue(getRes.stream().anyMatch(a -> a.id2 == 4));
    }

    // ---------- v2 improvement 1: cursor-based pagination (FOLLOW-UPS.md #1) ----------

    @Test
    public void testCursorPaginationWalksFullListOnceInOrder() {
        makeStack();
        // 20 edges with distinct, increasing timestamps.
        for (int i = 0; i < 20; i++) {
            follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 100 + i, 1000 + i, ""));
        }

        List<Long> seen = new ArrayList<>();
        String cursor = null;
        int pages = 0;
        while (true) {
            SocialGraphEngineTao.Page page = engine.assocPage(1, 1, 6, cursor);
            for (SocialGraphEngineTao.Association a : page.edges) {
                seen.add(a.id2);
            }
            pages++;
            cursor = page.nextCursor;
            if (cursor == null) {
                break;
            }
        }

        // Pages of 6, 6, 6, 2; newest first; no duplicates, none lost.
        assertEquals(4, pages);
        assertEquals(20, seen.size());
        assertEquals(20, new HashSet<>(seen).size());
        for (int i = 0; i + 1 < seen.size(); i++) {
            assertTrue(seen.get(i) > seen.get(i + 1));
        }
    }

    @Test
    public void testCursorPaginationTieBreaksOnId2() {
        makeStack();
        // Same timestamp on every edge forces the id2 tie-break in the cursor.
        for (long id2 : new long[]{5, 3, 9, 7}) {
            follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, id2, 1000, ""));
        }

        SocialGraphEngineTao.Page first = engine.assocPage(1, 1, 2, null);
        assertEquals(9, first.edges.get(0).id2);
        assertEquals(7, first.edges.get(1).id2);

        SocialGraphEngineTao.Page second = engine.assocPage(1, 1, 2, first.nextCursor);
        assertEquals(5, second.edges.get(0).id2);
        assertEquals(3, second.edges.get(1).id2);
        assertNull(second.nextCursor);
    }

    @Test
    public void testCursorPaginationEmptyForUnknownList() {
        makeStack();
        SocialGraphEngineTao.Page page = engine.assocPage(42, 1, 5, null);
        assertTrue(page.edges.isEmpty());
        assertNull(page.nextCursor);
    }

    // ---------- v2 improvement 2: read-your-writes versioning (FOLLOW-UPS.md #2) ----------

    @Test
    public void testVersionsBumpOnEveryWrite() {
        makeStack();

        long v1 = follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 2, 1000, ""));
        long v2 = follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 3, 1001, ""));
        long v3 = follower.deleteAssociation(1, 1, 2);

        assertEquals(1, v1);
        assertEquals(2, v2);
        assertEquals(3, v3);
        assertEquals(3, leader.getVersion(1, 1));
    }

    @Test
    public void testReadYourWritesSurvivesInvalidationBusLag() {
        SocialGraphEngineTao.Database db = new SocialGraphEngineTao.Database();
        SocialGraphEngineTao.LeaderCache leader = new SocialGraphEngineTao.LeaderCache(db);
        SocialGraphEngineTao.FollowerCache writer = new SocialGraphEngineTao.FollowerCache(leader);
        SocialGraphEngineTao.FollowerCache lagging = new SocialGraphEngineTao.FollowerCache(leader);

        writer.addAssociation(new SocialGraphEngineTao.Association(1, 1, 2, 1000, ""));
        lagging.getAssociations(1, 1); // pull the v1 list into the lagging region

        // Wormhole goes down for the lagging region, then a write lands:
        // the invalidation message never reaches it.
        lagging.setBusConnected(false);
        long newVersion = writer.addAssociation(new SocialGraphEngineTao.Association(1, 1, 3, 1001, ""));
        assertEquals(2, newVersion);

        // A plain read serves the stale entry.
        List<SocialGraphEngineTao.Association> stale = lagging.getAssociations(1, 1);
        assertEquals(1, stale.size());

        // The client stored the write's version; sending it as minVersion
        // force-bypasses the stale cache entry (FOLLOW-UPS.md #2).
        List<SocialGraphEngineTao.Association> fresh = lagging.getAssociations(1, 1, newVersion);
        assertEquals(2, fresh.size());
        assertTrue(fresh.stream().anyMatch(a -> a.id2 == 2));
        assertTrue(fresh.stream().anyMatch(a -> a.id2 == 3));
    }

    // ---------- v2 improvement 3: inverse edge writes (FOLLOW-UPS.md variants #1) ----------

    @Test
    public void testInverseEdgesServeBothDirections() {
        makeStack();
        int FOLLOWS = 1, FOLLOWED_BY = 2;

        engine.addInverseAssociation(1, FOLLOWS, 2, FOLLOWED_BY, 1000, "");
        engine.addInverseAssociation(3, FOLLOWS, 2, FOLLOWED_BY, 1001, "");

        List<SocialGraphEngineTao.Association> following = follower.getAssociations(1, FOLLOWS);
        assertEquals(1, following.size());
        assertEquals(2, following.get(0).id2);

        List<SocialGraphEngineTao.Association> followersOf2 = follower.getAssociations(2, FOLLOWED_BY);
        assertEquals(2, followersOf2.size());
        assertTrue(followersOf2.stream().anyMatch(a -> a.id2 == 1));
        assertTrue(followersOf2.stream().anyMatch(a -> a.id2 == 3));
    }

    @Test
    public void testInverseDeleteRemovesBothDirections() {
        makeStack();
        int FOLLOWS = 1, FOLLOWED_BY = 2;

        engine.addInverseAssociation(1, FOLLOWS, 2, FOLLOWED_BY, 1000, "");
        assertEquals(1, follower.assocCount(2, FOLLOWED_BY));

        engine.deleteInverseAssociation(1, FOLLOWS, 2, FOLLOWED_BY);
        assertEquals(0, follower.assocCount(1, FOLLOWS));
        assertEquals(0, follower.assocCount(2, FOLLOWED_BY));
    }
}
