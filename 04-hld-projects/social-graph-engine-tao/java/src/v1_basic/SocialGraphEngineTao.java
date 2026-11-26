package v1_basic;

import java.util.*;

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

    public static class Database {
        public Map<Long, ObjectNode> objects = new HashMap<>();
        // Map from "id1:atype:bucketId" -> List of Associations
        public Map<String, List<Association>> associations = new HashMap<>();

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

        public void addAssociation(Association assoc) {
            int bucketId = getBucketId(assoc.id1, assoc.id2);
            String key = assoc.id1 + ":" + assoc.atype + ":" + bucketId;
            associations.computeIfAbsent(key, k -> new ArrayList<>()).add(assoc);
            associations.get(key).sort((a, b) -> Long.compare(b.timestamp, a.timestamp));
        }

        public void deleteAssociation(long id1, int atype, long id2) {
            int bucketId = getBucketId(id1, id2);
            String key = id1 + ":" + atype + ":" + bucketId;
            if (associations.containsKey(key)) {
                associations.get(key).removeIf(a -> a.id2 == id2);
            }
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
            results.sort((a, b) -> Long.compare(b.timestamp, a.timestamp));
            return results;
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

        public void addAssociation(Association assoc) {
            db.addAssociation(assoc);
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
                    cache.get(key).sort((a, b) -> Long.compare(b.timestamp, a.timestamp));
                }
            }
            broadcastInvalidation(assoc.id1, assoc.atype);
        }

        public void deleteAssociation(long id1, int atype, long id2) {
            db.deleteAssociation(id1, atype, id2);
            String key = id1 + ":" + atype;
            if (cache.containsKey(key)) {
                cache.get(key).removeIf(a -> a.id2 == id2);
            }
            broadcastInvalidation(id1, atype);
        }

        public List<Association> getAssociations(long id1, int atype) {
            String key = id1 + ":" + atype;
            if (!cache.containsKey(key)) {
                cache.put(key, new ArrayList<>(db.getAssociations(id1, atype)));
            }
            return cache.get(key);
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
        private LeaderCache leader;
        public Map<String, List<Association>> cache = new HashMap<>();

        public FollowerCache(LeaderCache leader) {
            this.leader = leader;
            this.leader.registerFollower(this);
        }

        public void invalidate(long id1, int atype) {
            String key = id1 + ":" + atype;
            cache.remove(key);
        }

        public void addAssociation(Association assoc) {
            leader.addAssociation(assoc);
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
                    cache.get(key).sort((a, b) -> Long.compare(b.timestamp, a.timestamp));
                }
            }
        }

        public void deleteAssociation(long id1, int atype, long id2) {
            leader.deleteAssociation(id1, atype, id2);
            String key = id1 + ":" + atype;
            if (cache.containsKey(key)) {
                cache.get(key).removeIf(a -> a.id2 == id2);
            }
        }

        public List<Association> getAssociations(long id1, int atype) {
            String key = id1 + ":" + atype;
            if (!cache.containsKey(key)) {
                cache.put(key, new ArrayList<>(leader.getAssociations(id1, atype)));
            }
            return cache.get(key);
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
    }
}
