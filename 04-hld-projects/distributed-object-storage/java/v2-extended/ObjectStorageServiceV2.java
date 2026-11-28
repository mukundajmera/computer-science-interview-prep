import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

/**
 * v2-extended distributed object storage simulator.
 *
 * Improvements over v1-basic (each has dedicated tests):
 *
 * 1. Throttled background repair with failure injection: FOLLOW-UPS.md #3
 *    requires chunk rebuilds to be rate-limited so they do not degrade user
 *    reads and writes. ChunkServerV2 can simulate single-chunk loss and
 *    whole server downtime, and repairPass(long) re-replicates
 *    under-replicated chunks under an explicit byte budget per sweep.
 *
 * 2. Self-describing container format with index rebuild: the FOLLOW-UPS.md
 *    interviewer probe asks what happens when a chunk server's local index
 *    is corrupted. v2 frames every chunk with a magic header (see
 *    ChunkServerV2) so rebuildIndexFromContainer() can reconstruct the index
 *    by scanning the container, and startup always rebuilds from disk.
 *
 * 3. Configurable version retention with garbage collection: v1's
 *    compaction test had to drop old versions by hand ("in a real system
 *    this might be based on age. Here we'll clear ... manually"). v2 adds a
 *    keep-latest-N retention policy and collectGarbage() so compaction
 *    actually reclaims the space held by superseded versions.
 */
public class ObjectStorageServiceV2 {

    private final MetadataStoreV2 metadataStore;
    private final List<ChunkServerV2> chunkServers;
    private final int replicationFactor = 3;
    private final ReentrantLock lock = new ReentrantLock();
    private final Map<String, MultipartUploadInfo> multipartUploads = new ConcurrentHashMap<>();
    private final Integer retentionKeepLatest;

    private static class MultipartUploadInfo {
        String bucket;
        String key;
        Map<Integer, ChunkMeta> parts = new TreeMap<>();

        MultipartUploadInfo(String bucket, String key) {
            this.bucket = bucket;
            this.key = key;
        }
    }

    private static class ChunkMeta {
        String chunkId;
        int size;

        ChunkMeta(String chunkId, int size) {
            this.chunkId = chunkId;
            this.size = size;
        }
    }

    public ObjectStorageServiceV2(String dataDir) throws IOException {
        this(dataDir, null);
    }

    public ObjectStorageServiceV2(String dataDir, Integer retentionKeepLatest) throws IOException {
        this.metadataStore = new MetadataStoreV2();
        this.chunkServers = new ArrayList<>();
        for (int i = 0; i < replicationFactor; i++) {
            this.chunkServers.add(new ChunkServerV2(dataDir, "server_" + i));
        }
        this.retentionKeepLatest = retentionKeepLatest;
    }

    public MetadataStoreV2 getMetadataStore() {
        return metadataStore;
    }

    public List<ChunkServerV2> getChunkServers() {
        return chunkServers;
    }

    public void createBucket(String bucketName) {
        metadataStore.createBucket(bucketName);
    }

    private List<ChunkServerV2> getReplicas(String chunkId) {
        int hashVal = Math.abs(chunkId.hashCode());
        List<ChunkServerV2> replicas = new ArrayList<>();
        for (int i = 0; i < replicationFactor; i++) {
            replicas.add(chunkServers.get((hashVal + i) % chunkServers.size()));
        }
        return replicas;
    }

    private void writeChunkReplicas(String chunkId, byte[] data) throws IOException {
        List<ChunkServerV2> replicas = getReplicas(chunkId);
        int successCount = 0;
        for (ChunkServerV2 replica : replicas) {
            if (replica.isDown()) {
                continue;
            }
            try {
                replica.writeChunk(chunkId, data);
                successCount++;
            } catch (IllegalArgumentException e) {
                if (e.getMessage() != null && e.getMessage().contains("already exists")) {
                    successCount++;
                }
            }
        }
        if (successCount == 0) {
            throw new RuntimeException("Failed to write chunk to any replica");
        }
    }

    public String putObject(String bucketName, String objKey, byte[] data) throws IOException {
        String versionId = UUID.randomUUID().toString();
        String chunkId = bucketName + "_" + objKey + "_" + versionId + "_0";
        writeChunkReplicas(chunkId, data);
        MetadataStoreV2.ObjectMetadata metadata =
                new MetadataStoreV2.ObjectMetadata(objKey, versionId, false);
        metadata.chunks.add(chunkId);
        metadata.size = data.length;
        metadataStore.putObjectMetadata(bucketName, objKey, metadata);
        return versionId;
    }

    public byte[] getObject(String bucketName, String objKey, String versionId) throws IOException {
        MetadataStoreV2.ObjectMetadata metadata = metadataStore.getObjectMetadata(bucketName, objKey, versionId);
        if (metadata == null || metadata.isDeleteMarker) {
            return null;
        }
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        for (String chunkId : metadata.chunks) {
            List<ChunkServerV2> replicas = getReplicas(chunkId);
            byte[] chunkData = null;
            for (ChunkServerV2 replica : replicas) {
                if (replica.isDown()) {
                    continue;
                }
                try {
                    chunkData = replica.readChunk(chunkId);
                    break;
                } catch (IllegalArgumentException | IllegalStateException e) {
                    // Try next replica
                }
            }
            if (chunkData == null) {
                throw new RuntimeException("Data loss: Chunk " + chunkId
                        + " unavailable or corrupt on all replicas");
            }
            outputStream.write(chunkData);
            // Read repair for replicas that are up but missing or corrupt.
            for (ChunkServerV2 replica : replicas) {
                if (replica.isDown()) {
                    continue;
                }
                try {
                    replica.readChunk(chunkId);
                } catch (IllegalArgumentException | IllegalStateException | IOException e) {
                    replica.repairChunk(chunkId, chunkData);
                }
            }
        }
        return outputStream.toByteArray();
    }

    public byte[] getObject(String bucketName, String objKey) throws IOException {
        return getObject(bucketName, objKey, null);
    }

    public String deleteObject(String bucketName, String objKey) {
        String versionId = UUID.randomUUID().toString();
        MetadataStoreV2.ObjectMetadata metadata =
                new MetadataStoreV2.ObjectMetadata(objKey, versionId, true);
        metadataStore.putObjectMetadata(bucketName, objKey, metadata);
        return versionId;
    }

    public String initiateMultipartUpload(String bucketName, String objKey) {
        lock.lock();
        try {
            String uploadId = UUID.randomUUID().toString();
            multipartUploads.put(uploadId, new MultipartUploadInfo(bucketName, objKey));
            return uploadId;
        } finally {
            lock.unlock();
        }
    }

    public void uploadPart(String uploadId, int partNumber, byte[] data) throws IOException {
        MultipartUploadInfo uploadInfo;
        lock.lock();
        try {
            uploadInfo = multipartUploads.get(uploadId);
            if (uploadInfo == null) {
                throw new IllegalArgumentException("Invalid upload ID");
            }
        } finally {
            lock.unlock();
        }
        String chunkId = uploadInfo.bucket + "_" + uploadInfo.key + "_" + uploadId + "_" + partNumber;
        writeChunkReplicas(chunkId, data);
        lock.lock();
        try {
            if (multipartUploads.containsKey(uploadId)) {
                multipartUploads.get(uploadId).parts.put(partNumber, new ChunkMeta(chunkId, data.length));
            } else {
                throw new IllegalArgumentException("Upload ID was completed or cancelled");
            }
        } finally {
            lock.unlock();
        }
    }

    public String completeMultipartUpload(String uploadId) {
        MultipartUploadInfo uploadInfo;
        lock.lock();
        try {
            uploadInfo = multipartUploads.remove(uploadId);
            if (uploadInfo == null) {
                throw new IllegalArgumentException("Invalid upload ID");
            }
        } finally {
            lock.unlock();
        }
        MetadataStoreV2.ObjectMetadata metadata =
                new MetadataStoreV2.ObjectMetadata(uploadInfo.key, uploadId, false);
        long totalSize = 0;
        for (Map.Entry<Integer, ChunkMeta> entry : uploadInfo.parts.entrySet()) {
            metadata.chunks.add(entry.getValue().chunkId);
            totalSize += entry.getValue().size;
        }
        metadata.size = totalSize;
        metadataStore.putObjectMetadata(uploadInfo.bucket, uploadInfo.key, metadata);
        return uploadId;
    }

    public List<String> listObjects(String bucketName, String prefix) {
        return metadataStore.listObjects(bucketName, prefix);
    }

    public void compactStorage() throws IOException {
        Set<String> activeChunks = metadataStore.getAllActiveChunks();
        for (ChunkServerV2 server : chunkServers) {
            server.compact(activeChunks);
        }
    }

    /**
     * One throttled rebuild sweep (improvement #1, FOLLOW-UPS.md #3):
     * re-replicates every under-replicated active chunk it finds until the
     * per-sweep byte budget is spent, so background repair cannot saturate
     * the network during peak traffic. Returns the repaired chunk ids.
     */
    public List<String> repairPass(long byteBudget) throws IOException {
        List<String> repaired = new ArrayList<>();
        long spent = 0;
        Set<String> active = new TreeSet<>(metadataStore.getAllActiveChunks());
        for (String chunkId : active) {
            List<ChunkServerV2> replicas = getReplicas(chunkId);
            ChunkServerV2 holder = null;
            ChunkServerV2 missing = null;
            for (ChunkServerV2 replica : replicas) {
                if (replica.isDown()) {
                    continue;
                }
                if (replica.hasChunk(chunkId)) {
                    if (holder == null) {
                        holder = replica;
                    }
                } else if (missing == null) {
                    missing = replica;
                }
            }
            if (holder == null || missing == null) {
                continue;
            }
            byte[] data = holder.readChunk(chunkId);
            if (spent + data.length > byteBudget) {
                break;
            }
            missing.repairChunk(chunkId, data);
            spent += data.length;
            repaired.add(chunkId);
        }
        return repaired;
    }

    /** Unbounded repair sweep. */
    public List<String> repairPass() throws IOException {
        return repairPass(Long.MAX_VALUE);
    }

    /**
     * Version-retention GC (improvement #3): prunes superseded versions per
     * the keep-latest-N policy, then compacts every container so the pruned
     * chunks' space is actually reclaimed. Returns the pruned chunks. The
     * newest version of each object always survives, so a trailing delete
     * marker keeps the object deleted.
     */
    public List<String> collectGarbage(Integer keepLatest) throws IOException {
        Integer keep = keepLatest != null ? keepLatest : retentionKeepLatest;
        if (keep == null) {
            throw new IllegalStateException(
                    "No retention policy: pass keepLatest or configure retentionKeepLatest");
        }
        List<String> pruned = metadataStore.pruneVersions(Math.max(1, keep));
        compactStorage();
        return pruned;
    }
}
