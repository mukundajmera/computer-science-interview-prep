package v1_basic;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Set;
import java.util.HashSet;

public class SocialGraphEngineTaoTest {

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
        SocialGraphEngineTao.Database db = new SocialGraphEngineTao.Database();
        SocialGraphEngineTao.LeaderCache leader = new SocialGraphEngineTao.LeaderCache(db);
        SocialGraphEngineTao.FollowerCache follower = new SocialGraphEngineTao.FollowerCache(leader);
        SocialGraphEngineTao.GraphEngine engine = new SocialGraphEngineTao.GraphEngine(db, leader, follower);
        
        long time = System.currentTimeMillis() / 1000;
        
        SocialGraphEngineTao.Association assoc1 = new SocialGraphEngineTao.Association(1, 1, 2, time, "");
        follower.addAssociation(assoc1);
        
        List<SocialGraphEngineTao.Association> assocs = follower.getAssociations(1, 1);
        assertEquals(1, assocs.size());
        assertEquals(2, assocs.get(0).id2);
        
        SocialGraphEngineTao.Association assoc2 = new SocialGraphEngineTao.Association(1, 1, 3, time + 1, "");
        follower.addAssociation(assoc2);
        
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
        
        // f1 reads, caching the empty list
        f1.getAssociations(1, 1);
        assertTrue(f1.cache.containsKey("1:1"));
        
        // f2 writes
        SocialGraphEngineTao.Association assoc = new SocialGraphEngineTao.Association(1, 1, 2, time, "");
        f2.addAssociation(assoc);
        
        // f1 cache should be invalidated
        assertFalse(f1.cache.containsKey("1:1"));
        
        // Next read by f1 should miss and fetch from leader
        List<SocialGraphEngineTao.Association> assocs = f1.getAssociations(1, 1);
        assertEquals(1, assocs.size());
        assertEquals(2, assocs.get(0).id2);
    }

    @Test
    public void testMutualFriends() {
        SocialGraphEngineTao.Database db = new SocialGraphEngineTao.Database();
        SocialGraphEngineTao.LeaderCache leader = new SocialGraphEngineTao.LeaderCache(db);
        SocialGraphEngineTao.FollowerCache follower = new SocialGraphEngineTao.FollowerCache(leader);
        SocialGraphEngineTao.GraphEngine engine = new SocialGraphEngineTao.GraphEngine(db, leader, follower);
        
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
        SocialGraphEngineTao.Database db = new SocialGraphEngineTao.Database();
        SocialGraphEngineTao.LeaderCache leader = new SocialGraphEngineTao.LeaderCache(db);
        SocialGraphEngineTao.FollowerCache follower = new SocialGraphEngineTao.FollowerCache(leader);
        
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
        SocialGraphEngineTao.Database db = new SocialGraphEngineTao.Database();
        SocialGraphEngineTao.LeaderCache leader = new SocialGraphEngineTao.LeaderCache(db);
        SocialGraphEngineTao.FollowerCache follower = new SocialGraphEngineTao.FollowerCache(leader);
        
        long baseTime = 1000;
        follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 2, baseTime, ""));
        follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 3, baseTime + 10, ""));
        follower.addAssociation(new SocialGraphEngineTao.Association(1, 1, 4, baseTime + 20, ""));
        
        // assocCount
        assertEquals(3, follower.assocCount(1, 1));
        
        // assocRange
        List<SocialGraphEngineTao.Association> rangeRes = follower.assocRange(1, 1, baseTime + 5, baseTime + 25);
        assertEquals(2, rangeRes.size());
        assertTrue(rangeRes.stream().anyMatch(a -> a.id2 == 3));
        assertTrue(rangeRes.stream().anyMatch(a -> a.id2 == 4));
        
        // assocGet
        Set<Long> ids = new HashSet<>();
        ids.add(2L);
        ids.add(4L);
        List<SocialGraphEngineTao.Association> getRes = follower.assocGet(1, 1, ids);
        assertEquals(2, getRes.size());
        assertTrue(getRes.stream().anyMatch(a -> a.id2 == 2));
        assertTrue(getRes.stream().anyMatch(a -> a.id2 == 4));
    }
}
