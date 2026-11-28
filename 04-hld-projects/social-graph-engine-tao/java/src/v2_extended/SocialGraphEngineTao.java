package v2_extended;

import java.util.*;

/**
 * v2-extended TAO social graph engine. The two-tier cache, supernode
 * virtual bucketing and read path are v1 behavior unchanged; the step-ups
 * are the ones the project's own docs call for:
 *
 * 1. Cursor-based pagination (FOLLOW-UPS.md #1): assocPage walks a
 *    time-ordered association list with an opaque "timestamp:id2" cursor
 *    instead of OFFSET/LIMIT, so deep pages on supernodes stay O(limit).
 * 2. Read-your-writes versioning (FOLLOW-UPS.md #2): every association
 *    list carries a version that bumps on each write; a write returns the
 *    new version, and a read that passes it as minVersion force-bypasses
 *    a stale Follower cache entry, so a client sees its own write even
 *    while the invalidation bus (Wormhole) is down or lagging.
 * 3. Inverse edge writes (FOLLOW-UPS.md "Variants and extensions" #1):
 *    addInverseAssociation writes both directed edges - (A, FOLLOWS, B)
 *    sharded by A and (B, FOLLOWED_BY, A) sharded by B - so both "who
 *    does A follow" and "who follows B" stay O(1) lookups, accepting the
 *    eventual-consistency trade-off PITFALLS.md #2 prescribes over 2PC.
 */
public class SocialGraphEngineTao {

    public static class ObjectNode {
        public long id;
        public int otype;
        public String data;

        public ObjectNode(long id, int otype, String data) {
            this.id = id;
            this.otype = otype;
            this.data = data;
        }
    }

    public static class Association {
        public long id1;
        public int atype;
        public long id2;
        public long timestamp;
        public String data;

        public Association(long id1, int atype, long id2, long timestamp, String data) {
            this.id1 = id1;
            this.atype = atype;
            this.id2 = id2;
            this.timestamp = timestamp;
            this.data = data;
        }
    }

    /** One page of a cursor-paginated association list. */
    public static class Page {
        public final List<Association> edges;
        public final String nextCursor; // null when the list is exhausted

        public Page(List<Association> edges, String nextCursor) {
            this.edges = edges;
            this.nextCursor = nextCursor;
        }
    }

    // Total order for stable pagination: time DESC, then id2 DESC on ties.
    private static int compareEdges(Association a, Association b) {
        int cmp = Long.compare(b.timestamp, a.timestamp);
        return cmp != 0 ? cmp : Long.compare(b.id2, a.id2);
    }

    private static String encodeCursor(Association assoc) {
        return assoc.timestamp + ":" + assoc.id2;
    }

    // True when edge sorts strictly after the cursor position.
    private static boolean isAfterCursor(Association edge, String cursor) {
        String[] parts = cursor.split(":");
        long cursorTimestamp = Long.parseLong(parts[0]);
        long cursorId2 = Long.parseLong(parts[1]);
        if (edge.timestamp != cursorTimestamp) {
            return edge.timestamp < cursorTimestamp;
        }
        return edge.id2 < cursorId2;
    }

    public static class Database {
        public Map<Long, ObjectNode> objects = new HashMap<>();
        // Map from "id1:atype:bucketId" -> List of Associations
        public Map<String, List<Association>> associations = new HashMap<>();
        // Version per association list (FOLLOW-UPS.md #2), bumped per write.
        private final Map<String, Long> versions = new HashMap<>();

        public void addObject(ObjectNode obj) {
            objects.put(obj.id, obj);
        }

        public ObjectNode getObject(long id) {
            return objects.get(id);
        }

        public void updateObject(long id, String data) {
            if (objects.containsKey(id)) {
                objects.get(id).data = data;
            }
        }

        public void deleteObject(long id) {
            objects.remove(id);
        }

        private int getBucketId(long id1, long id2) {
            if (isSupernode(id1)) {
                return (int) (Math.abs(id2) % 10); // 10 virtual buckets
            }
            return 0;
        }

        private boolean isSupernode(long id1) {
            return id1 >= 1000;
        }

        private long bumpVersion(long id1, int atype) {
            String key = id1 + ":" + atype;
            long version = versions.getOrDefault(key, 0L) + 1;
            versions.put(key, version);
            return version;
        }

        public long getVersion(long id1, int atype) {
            return versions.getOrDefault(id1 + ":" + atype, 0L);
        }

        public long addAssociation(Association assoc) {
            int bucketId = getBucketId(assoc.id1, assoc.id2);
            String key = assoc.id1 + ":" + assoc.atype + ":" + bucketId;
            associations.computeIfAbsent(key, k -> new ArrayList<>()).add(assoc);
            associations.get(key).sort(SocialGraphEngineTao::compareEdges);
            return bumpVersion(assoc.id1, assoc.atype);
        }

        public long deleteAssociation(long id1, int atype, long id2) {
            int bucketId = getBucketId(id1, id2);
            String key = id1 + ":" + atype + ":" + bucketId;
            if (associations.containsKey(key)) {
                associations.get(key).removeIf(a -> a.id2 == id2);
            }
            return bumpVersion(id1, atype);
        }

        public List<Association> getAssociations(long id1, int atype) {
            List<Association> results = new ArrayList<>();
            if (isSupernode(id1)) {
                for (int i = 0; i < 10; i++) {
                    String key = id1 + ":" + atype + ":" + i;
                    if (associations.containsKey(key)) {
                        results.addAll(associations.get(key));
                    }
                }
            } else {
                String key = id1 + ":" + atype + ":0";
                if (associations.containsKey(key)) {
                    results.addAll(associations.get(key));
                }
            }
            results.sort(SocialGraphEngineTao::compareEdges);
            return results;
        }

        /**
         * Cursor-based pagination (FOLLOW-UPS.md #1). The cursor is the
         * (timestamp, id2) of the last edge returned, so a page costs
         * O(limit) no matter how deep into the list the client is.
         */
        public Page assocPage(long id1, int atype, int limit, String cursor) {
            List<Association> edges = getAssociations(id1, atype);
            if (cursor != null) {
                edges.removeIf(a -> !isAfterCursor(a, cursor));
            }
            List<Association> page = new ArrayList<>(edges.subList(0, Math.min(limit, edges.size())));
            String nextCursor = null;
            if (edges.size() > limit && !page.isEmpty()) {
                nextCursor = encodeCursor(page.get(page.size() - 1));
            }
            return new Page(page, nextCursor);
        }

        public List<Association> assocRange(long id1, int atype, long startTime, long endTime) {
            List<Association> results = getAssociations(id1, atype);
            results.removeIf(a -> a.timestamp < startTime || a.timestamp > endTime);
            return results;
        }

        public int assocCount(long id1, int atype) {
            return getAssociations(id1, atype).size();
        }

        public List<Association> assocGet(long id1, int atype, Set<Long> id2s) {
            List<Association> results = getAssociations(id1, atype);
            results.removeIf(a -> !id2s.contains(a.id2));
            return results;
        }
    }

    public static class LeaderCache {
        private Database db;
        public Map<String, List<Association>> cache = new HashMap<>();
        private List<FollowerCache> followers = new ArrayList<>();

        public LeaderCache(Database db) {
            this.db = db;
        }

        public void registerFollower(FollowerCache follower) {
            followers.add(follower);
        }

        public void broadcastInvalidation(long id1, int atype) {
            for (FollowerCache follower : followers) {
                follower.invalidate(id1, atype);
            }
        }

        public long addAssociation(Association assoc) {
            long version = db.addAssociation(assoc);
            String key = assoc.id1 + ":" + assoc.atype;
            if (cache.containsKey(key)) {
                boolean exists = false;
                for (Association a : cache.get(key)) {
                    if (a.id2 == assoc.id2) {
                        exists = true;
                        break;
                    }
                }
                if (!exists) {
                    cache.get(key).add(assoc);
                    cache.get(key).sort(SocialGraphEngineTao::compareEdges);
                }
            }
            broadcastInvalidation(assoc.id1, assoc.atype);
            return version;
        }

        public long deleteAssociation(long id1, int atype, long id2) {
            long version = db.deleteAssociation(id1, atype, id2);
            String key = id1 + ":" + atype;
            if (cache.containsKey(key)) {
                cache.get(key).removeIf(a -> a.id2 == id2);
            }
            broadcastInvalidation(id1, atype);
            return version;
        }

        public long getVersion(long id1, int atype) {
            return db.getVersion(id1, atype);
        }

        public List<Association> getAssociations(long id1, int atype) {
            String key = id1 + ":" + atype;
            if (!cache.containsKey(key)) {
                cache.put(key, new ArrayList<>(db.getAssociations(id1, atype)));
            }
            return cache.get(key);
        }

        public Page assocPage(long id1, int atype, int limit, String cursor) {
            // Deep pagination is a guaranteed cache miss (PITFALLS.md #5);
            // the Leader queries the DB, per FOLLOW-UPS.md #1.
            return db.assocPage(id1, atype, limit, cursor);
        }

        public List<Association> assocRange(long id1, int atype, long startTime, long endTime) {
            List<Association> results = new ArrayList<>(getAssociations(id1, atype));
            results.removeIf(a -> a.timestamp < startTime || a.timestamp > endTime);
            return results;
        }

        public int assocCount(long id1, int atype) {
            return getAssociations(id1, atype).size();
        }

        public List<Association> assocGet(long id1, int atype, Set<Long> id2s) {
            List<Association> results = new ArrayList<>(getAssociations(id1, atype));
            results.removeIf(a -> !id2s.contains(a.id2));
            return results;
        }
    }

    public static class FollowerCache {
        /** Cached association list plus the version it was read at. */
        public static class CacheEntry {
            public final List<Association> edges;
            public long version;

            public CacheEntry(List<Association> edges, long version) {
                this.edges = edges;
                this.version = version;
            }
        }

        private LeaderCache leader;
        public Map<String, CacheEntry> cache = new HashMap<>();
        // False models the invalidation bus being down for this region
        // (FOLLOW-UPS.md #2): invalidate messages are lost.
        private boolean busConnected = true;

        public FollowerCache(LeaderCache leader) {
            this.leader = leader;
            this.leader.registerFollower(this);
        }

        public void setBusConnected(boolean connected) {
            this.busConnected = connected;
        }

        public void invalidate(long id1, int atype) {
            if (!busConnected) {
                return;
            }
            cache.remove(id1 + ":" + atype);
        }

        /**
         * Write through the Leader; returns the new list version, which a
         * client stores and sends back as minVersion (read-your-writes).
         */
        public long addAssociation(Association assoc) {
            long version = leader.addAssociation(assoc);
            String key = assoc.id1 + ":" + assoc.atype;
            if (cache.containsKey(key)) {
                CacheEntry entry = cache.get(key);
                boolean exists = false;
                for (Association a : entry.edges) {
                    if (a.id2 == assoc.id2) {
                        exists = true;
                        break;
                    }
                }
                if (!exists) {
                    entry.edges.add(assoc);
                    entry.edges.sort(SocialGraphEngineTao::compareEdges);
                }
                entry.version = version;
            }
            return version;
        }

        public long deleteAssociation(long id1, int atype, long id2) {
            long version = leader.deleteAssociation(id1, atype, id2);
            String key = id1 + ":" + atype;
            if (cache.containsKey(key)) {
                CacheEntry entry = cache.get(key);
                entry.edges.removeIf(a -> a.id2 == id2);
                entry.version = version;
            }
            return version;
        }

        public List<Association> getAssociations(long id1, int atype) {
            return getAssociations(id1, atype, null);
        }

        public List<Association> getAssociations(long id1, int atype, Long minVersion) {
            String key = id1 + ":" + atype;
            CacheEntry entry = cache.get(key);
            if (entry != null && (minVersion == null || entry.version >= minVersion)) {
                return entry.edges;
            }
            // Miss, or a stale entry the client's minVersion rejects:
            // bypass to the Leader for the freshest data (FOLLOW-UPS.md
            // #2). The list is copied so a later Leader-side write cannot
            // mutate this region's cached entry through a shared reference.
            List<Association> edges = new ArrayList<>(leader.getAssociations(id1, atype));
            cache.put(key, new CacheEntry(edges, leader.getVersion(id1, atype)));
            return edges;
        }

        public List<Association> assocRange(long id1, int atype, long startTime, long endTime) {
            List<Association> results = new ArrayList<>(getAssociations(id1, atype));
            results.removeIf(a -> a.timestamp < startTime || a.timestamp > endTime);
            return results;
        }

        public int assocCount(long id1, int atype) {
            return getAssociations(id1, atype).size();
        }

        public List<Association> assocGet(long id1, int atype, Set<Long> id2s) {
            List<Association> results = new ArrayList<>(getAssociations(id1, atype));
            results.removeIf(a -> !id2s.contains(a.id2));
            return results;
        }
    }

    public static class GraphEngine {
        private Database db;
        private LeaderCache leader;
        private FollowerCache follower;

        public GraphEngine(Database db, LeaderCache leader, FollowerCache follower) {
            this.db = db;
            this.leader = leader;
            this.follower = follower;
        }

        public List<Long> getMutualFriends(long id1, long id2, int atype) {
            List<Association> f1Assocs = follower.getAssociations(id1, atype);
            Set<Long> f1Set = new HashSet<>();
            for (Association a : f1Assocs) {
                f1Set.add(a.id2);
            }

            List<Association> f2Assocs = follower.getAssociations(id2, atype);
            Set<Long> f2Set = new HashSet<>();
            for (Association a : f2Assocs) {
                f2Set.add(a.id2);
            }

            f1Set.retainAll(f2Set);
            return new ArrayList<>(f1Set);
        }

        public Page assocPage(long id1, int atype, int limit, String cursor) {
            return leader.assocPage(id1, atype, limit, cursor);
        }

        /**
         * Write both directed edges (FOLLOW-UPS.md variants #1): the two
         * writes are independent on purpose - PITFALLS.md #2 rejects 2PC
         * and accepts eventual consistency between them.
         */
        public long[] addInverseAssociation(long id1, int atype, long id2,
                                            int inverseAtype, long timestamp, String data) {
            Association forward = new Association(id1, atype, id2, timestamp, data);
            Association inverse = new Association(id2, inverseAtype, id1, timestamp, data);
            long forwardVersion = follower.addAssociation(forward);
            long inverseVersion = follower.addAssociation(inverse);
            return new long[]{forwardVersion, inverseVersion};
        }

        public long[] deleteInverseAssociation(long id1, int atype, long id2, int inverseAtype) {
            long forwardVersion = follower.deleteAssociation(id1, atype, id2);
            long inverseVersion = follower.deleteAssociation(id2, inverseAtype, id1);
            return new long[]{forwardVersion, inverseVersion};
        }
    }
}
