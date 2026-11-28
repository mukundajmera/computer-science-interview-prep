import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.locks.ReentrantLock;

/** v1 metadata store plus keep-latest-N version pruning for GC. */
public class MetadataStoreV2 {

    public static class ObjectMetadata {
        public final String objKey;
        public final String versionId;
        public final boolean isDeleteMarker;
        public List<String> chunks;
        public long size;
        public final long timestamp;

        public ObjectMetadata(String objKey, String versionId, boolean isDeleteMarker) {
            this.objKey = objKey;
            this.versionId = versionId;
            this.isDeleteMarker = isDeleteMarker;
            this.chunks = new ArrayList<>();
            this.size = 0;
            this.timestamp = System.currentTimeMillis();
        }
    }

    private final ReentrantLock lock;
    private final Set<String> buckets;
    private final Map<String, Map<String, List<ObjectMetadata>>> objects;

    public MetadataStoreV2() {
        this.lock = new ReentrantLock();
        this.buckets = ConcurrentHashMap.newKeySet();
        this.objects = new ConcurrentHashMap<>();
    }

    public void createBucket(String bucketName) {
        lock.lock();
        try {
            if (buckets.contains(bucketName)) {
                throw new IllegalArgumentException("Bucket " + bucketName + " already exists");
            }
            buckets.add(bucketName);
            objects.put(bucketName, new ConcurrentHashMap<>());
        } finally {
            lock.unlock();
        }
    }

    public List<String> listBuckets() {
        return new ArrayList<>(buckets);
    }

    public void putObjectMetadata(String bucketName, String objKey, ObjectMetadata metadata) {
        lock.lock();
        try {
            if (!buckets.contains(bucketName)) {
                throw new IllegalArgumentException("Bucket " + bucketName + " does not exist");
            }
            Map<String, List<ObjectMetadata>> bucketObjects = objects.get(bucketName);
            bucketObjects.putIfAbsent(objKey, new CopyOnWriteArrayList<>());
            bucketObjects.get(objKey).add(metadata);
        } finally {
            lock.unlock();
        }
    }

    public ObjectMetadata getObjectMetadata(String bucketName, String objKey, String versionId) {
        lock.lock();
        try {
            if (!buckets.contains(bucketName) || !objects.get(bucketName).containsKey(objKey)) {
                return null;
            }
            List<ObjectMetadata> versions = objects.get(bucketName).get(objKey);
            if (versions.isEmpty()) {
                return null;
            }
            if (versionId != null) {
                for (ObjectMetadata v : versions) {
                    if (v.versionId.equals(versionId)) {
                        return v;
                    }
                }
                return null;
            }
            return versions.get(versions.size() - 1); // Latest version
        } finally {
            lock.unlock();
        }
    }

    public List<String> listObjects(String bucketName, String prefix) {
        lock.lock();
        try {
            if (!buckets.contains(bucketName)) {
                throw new IllegalArgumentException("Bucket " + bucketName + " does not exist");
            }
            List<String> result = new ArrayList<>();
            for (Map.Entry<String, List<ObjectMetadata>> entry : objects.get(bucketName).entrySet()) {
                String objKey = entry.getKey();
                List<ObjectMetadata> versions = entry.getValue();
                if (objKey.startsWith(prefix) && !versions.isEmpty()
                        && !versions.get(versions.size() - 1).isDeleteMarker) {
                    result.add(objKey);
                }
            }
            return result;
        } finally {
            lock.unlock();
        }
    }

    public Set<String> getAllActiveChunks() {
        lock.lock();
        try {
            Set<String> activeChunks = new HashSet<>();
            for (Map<String, List<ObjectMetadata>> bucketObjects : objects.values()) {
                for (List<ObjectMetadata> versions : bucketObjects.values()) {
                    for (ObjectMetadata version : versions) {
                        if (!version.isDeleteMarker) {
                            activeChunks.addAll(version.chunks);
                        }
                    }
                }
            }
            return activeChunks;
        } finally {
            lock.unlock();
        }
    }

    /**
     * Drops all but the newest keepLatest versions of every object. The
     * newest version is never pruned, so a trailing delete marker keeps the
     * object deleted. Returns the chunks the pruned versions held; they
     * become garbage once compaction runs.
     */
    public List<String> pruneVersions(int keepLatest) {
        lock.lock();
        try {
            List<String> prunedChunks = new ArrayList<>();
            for (Map<String, List<ObjectMetadata>> bucketObjects : objects.values()) {
                for (List<ObjectMetadata> versions : bucketObjects.values()) {
                    while (versions.size() > keepLatest) {
                        prunedChunks.addAll(versions.remove(0).chunks);
                    }
                }
            }
            return prunedChunks;
        } finally {
            lock.unlock();
        }
    }
}
