import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

public class ObjectStorageService {

    private final MetadataStore metadataStore;
    private final List<ChunkServer> chunkServers;
    private final int replicationFactor = 3;
    private final ReentrantLock lock = new ReentrantLock();
    private final Map<String, MultipartUploadInfo> multipartUploads = new ConcurrentHashMap<>();

    private static class MultipartUploadInfo {
        String bucket;
        String key;
        Map<Integer, ChunkMeta> parts = new TreeMap<>(); // Sorted parts
        
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

    public ObjectStorageService(String dataDir) throws IOException {
        this.metadataStore = new MetadataStore();
        this.chunkServers = new ArrayList<>();
        for (int i = 0; i < replicationFactor; i++) {
            this.chunkServers.add(new ChunkServer(dataDir, "server_" + i));
        }
    }

    public MetadataStore getMetadataStore() {
        return metadataStore;
    }

    public List<ChunkServer> getChunkServers() {
        return chunkServers;
    }

    public void createBucket(String bucketName) {
        metadataStore.createBucket(bucketName);
    }

    private List<ChunkServer> getReplicas(String chunkId) {
        int hashVal = Math.abs(chunkId.hashCode());
        List<ChunkServer> replicas = new ArrayList<>();
        for (int i = 0; i < replicationFactor; i++) {
            replicas.add(chunkServers.get((hashVal + i) % chunkServers.size()));
        }
        return replicas;
    }

    private void writeChunkReplicas(String chunkId, byte[] data) throws IOException {
        List<ChunkServer> replicas = getReplicas(chunkId);
        int successCount = 0;
        
        for (ChunkServer replica : replicas) {
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
        
        MetadataStore.ObjectMetadata metadata = new MetadataStore.ObjectMetadata(objKey, versionId, false);
        metadata.chunks.add(chunkId);
        metadata.size = data.length;
        
        metadataStore.putObjectMetadata(bucketName, objKey, metadata);
        return versionId;
    }

    public byte[] getObject(String bucketName, String objKey, String versionId) throws IOException {
        MetadataStore.ObjectMetadata metadata = metadataStore.getObjectMetadata(bucketName, objKey, versionId);
        
        if (metadata == null || metadata.isDeleteMarker) {
            return null;
        }
        
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        
        for (String chunkId : metadata.chunks) {
            List<ChunkServer> replicas = getReplicas(chunkId);
            byte[] chunkData = null;
            ChunkServer validReplica = null;
            
            for (ChunkServer replica : replicas) {
                try {
                    chunkData = replica.readChunk(chunkId);
                    validReplica = replica;
                    break;
                } catch (IllegalArgumentException | IllegalStateException e) {
                    // Try next replica
                }
            }
            
            if (chunkData == null) {
                throw new RuntimeException("Data loss: Chunk " + chunkId + " unavailable or corrupt on all replicas");
            }
            
            outputStream.write(chunkData);
            
            // Read repair
            for (ChunkServer replica : replicas) {
                if (replica != validReplica) {
                    try {
                        replica.readChunk(chunkId);
                    } catch (IllegalArgumentException | IllegalStateException | IOException e) {
                        replica.repairChunk(chunkId, chunkData);
                    }
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
        MetadataStore.ObjectMetadata metadata = new MetadataStore.ObjectMetadata(objKey, versionId, true);
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
            // Need to verify it's still there after unlocking to do the write
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
        
        String versionId = uploadId;
        MetadataStore.ObjectMetadata metadata = new MetadataStore.ObjectMetadata(uploadInfo.key, versionId, false);
        
        long totalSize = 0;
        for (Map.Entry<Integer, ChunkMeta> entry : uploadInfo.parts.entrySet()) {
            metadata.chunks.add(entry.getValue().chunkId);
            totalSize += entry.getValue().size;
        }
        metadata.size = totalSize;
        
        metadataStore.putObjectMetadata(uploadInfo.bucket, uploadInfo.key, metadata);
        return versionId;
    }

    public List<String> listObjects(String bucketName, String prefix) {
        return metadataStore.listObjects(bucketName, prefix);
    }

    public void compactStorage() throws IOException {
        Set<String> activeChunks = metadataStore.getAllActiveChunks();
        for (ChunkServer server : chunkServers) {
            server.compact(activeChunks);
        }
    }
}