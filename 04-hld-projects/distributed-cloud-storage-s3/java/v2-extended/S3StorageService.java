package v2_extended;

/**
 * v2-extended S3 storage service.
 *
 * Improvements over v1-basic (named per the repo rule v1-basic -> v2-extended):
 * 1. Data-chunks-before-metadata write path (PITFALLS #4): objects are split
 *    into chunks that are written to a simulated blob-node store FIRST; only
 *    after every chunk write is acknowledged is the object metadata
 *    committed. A failure injection hook simulates node write failures; a
 *    failed PUT leaves no dangling metadata and the orphan chunks are
 *    tracked for garbage collection.
 * 2. Integrity checking and a scrubber (FOLLOW-UPS #3, bitrot): every chunk
 *    is stored with a checksum and a replica. GET verifies the checksum and
 *    throws ChunkIntegrityError on silent corruption; scrub() detects
 *    corrupted primaries and repairs them from the replica.
 * 3. Multipart lifecycle expiry (FOLLOW-UPS #2): see
 *    MultipartUploadManager, which adds a TTL with an injectable clock and
 *    a sweep that reclaims abandoned uploads and their part data.
 */

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public class S3StorageService {

    public static final int DEFAULT_CHUNK_SIZE = 16; // bytes; small so tests exercise multi-chunk objects

    public static class ChunkIntegrityError extends RuntimeException {
        public ChunkIntegrityError(String message) { super(message); }
    }

    public static class InjectedWriteError extends RuntimeException {
        public InjectedWriteError(String message) { super(message); }
    }

    static class ChunkRecord {
        final String chunkId;
        byte[] data;
        final byte[] replica;
        final String checksum;

        ChunkRecord(String chunkId, byte[] data) {
            this.chunkId = chunkId;
            this.data = data;
            this.replica = Arrays.copyOf(data, data.length);
            this.checksum = md5Hex(data);
        }

        boolean primaryOk() {
            return md5Hex(data).equals(checksum);
        }
    }

    /** Simulated blob-node store: primary copy plus one replica per chunk,
     * with a write-failure injection hook and a corruption hook for scrub
     * tests. */
    public static class ChunkStore {
        public final Map<String, ChunkRecord> chunks = new HashMap<>();
        private int failNextWrites = 0;
        private int skipWrites = 0;

        /** Arm `count` simulated write failures, applied after `skip`
         * successful writes (so a failure can strike mid-stream). */
        public void injectWriteFailures(int count, int skip) {
            this.failNextWrites = count;
            this.skipWrites = skip;
        }

        public String put(byte[] data) {
            if (skipWrites > 0) {
                skipWrites--;
            } else if (failNextWrites > 0) {
                failNextWrites--;
                throw new InjectedWriteError("simulated blob-node write failure");
            }
            String chunkId = UUID.randomUUID().toString();
            chunks.put(chunkId, new ChunkRecord(chunkId, data));
            return chunkId;
        }

        public byte[] get(String chunkId) {
            ChunkRecord record = chunks.get(chunkId);
            if (record == null) {
                throw new IllegalArgumentException("Chunk not found: " + chunkId);
            }
            if (!record.primaryOk()) {
                throw new ChunkIntegrityError("checksum mismatch on chunk " + chunkId);
            }
            return record.data;
        }

        /** Test hook: flip one byte of the primary copy (bitrot). */
        public void corrupt(String chunkId) {
            ChunkRecord record = chunks.get(chunkId);
            byte[] flipped = Arrays.copyOf(record.data, record.data.length);
            flipped[0] ^= (byte) 0xFF;
            record.data = flipped;
        }

        /** Detect corrupted primaries and repair them from the replica.
         * Returns the number of chunks repaired. */
        public int scrub() {
            int repaired = 0;
            for (ChunkRecord record : chunks.values()) {
                if (!record.primaryOk()) {
                    record.data = Arrays.copyOf(record.replica, record.replica.length);
                    repaired++;
                }
            }
            return repaired;
        }

        public int free(List<String> chunkIds) {
            int freed = 0;
            for (String chunkId : chunkIds) {
                ChunkRecord record = chunks.remove(chunkId);
                if (record != null) {
                    freed += record.data.length;
                }
            }
            return freed;
        }
    }

    public static class ObjectMetadata {
        public final String key;
        public final String versionId;
        public final List<String> chunkIds;
        public final int size;
        public final boolean isDeleted;
        public final long lastModified;
        public final String etag;

        public ObjectMetadata(String key, String versionId, List<String> chunkIds,
                              int size, boolean isDeleted, String etag) {
            this.key = key;
            this.versionId = versionId;
            this.chunkIds = chunkIds != null ? chunkIds : new ArrayList<>();
            this.size = size;
            this.isDeleted = isDeleted;
            this.lastModified = System.currentTimeMillis();
            this.etag = etag;
        }
    }

    static class Bucket {
        final String name;
        final Map<String, List<ObjectMetadata>> objects = new HashMap<>();

        Bucket(String name) {
            this.name = name;
        }
    }

    private final Map<String, Bucket> buckets = new HashMap<>();
    public final ChunkStore chunkStore;
    private final int chunkSize;
    private final byte[] secretAccessKey = "test-secret-key".getBytes(StandardCharsets.UTF_8);
    private final Set<String> usedSignatures = new HashSet<>();
    /** Chunks written before a failed metadata commit, awaiting GC (v2 item 1). */
    public final List<String> orphanChunkIds = new ArrayList<>();

    public S3StorageService() {
        this(new ChunkStore(), DEFAULT_CHUNK_SIZE);
    }

    public S3StorageService(ChunkStore chunkStore, int chunkSize) {
        if (chunkSize < 1) {
            throw new IllegalArgumentException("chunkSize must be positive");
        }
        this.chunkStore = chunkStore;
        this.chunkSize = chunkSize;
    }

    // --- bucket operations (parity with v1) ---

    public void createBucket(String bucketName) {
        buckets.putIfAbsent(bucketName, new Bucket(bucketName));
    }

    public void deleteBucket(String bucketName) {
        buckets.remove(bucketName);
    }

    // --- write path (v2 item 1: chunks first, metadata last) ---

    private String generateVersionId() {
        return UUID.randomUUID().toString();
    }

    private List<String> writeChunks(byte[] data) {
        List<String> chunkIds = new ArrayList<>();
        for (int offset = 0; offset < data.length; offset += chunkSize) {
            int end = Math.min(data.length, offset + chunkSize);
            chunkIds.add(chunkStore.put(Arrays.copyOfRange(data, offset, end)));
        }
        return chunkIds;
    }

    public String putObject(String bucketName, String key, byte[] data) {
        if (!buckets.containsKey(bucketName)) {
            throw new IllegalArgumentException("Bucket not found");
        }
        return commitObject(bucketName, key, data, md5Hex(data));
    }

    private String commitObject(String bucketName, String key, byte[] data, String etag) {
        // v2 item 1: write every data chunk and gather acks BEFORE metadata.
        Set<String> writtenBefore = new HashSet<>(chunkStore.chunks.keySet());
        List<String> chunkIds;
        try {
            chunkIds = writeChunks(data);
        } catch (InjectedWriteError e) {
            // No metadata is committed, so no GET can ever see this object;
            // the partial chunks are tracked as orphans for the GC sweep.
            for (String id : chunkStore.chunks.keySet()) {
                if (!writtenBefore.contains(id)) {
                    orphanChunkIds.add(id);
                }
            }
            throw e;
        }

        Bucket bucket = buckets.get(bucketName);
        String versionId = generateVersionId();
        ObjectMetadata obj = new ObjectMetadata(key, versionId, chunkIds, data.length, false, etag);
        bucket.objects.computeIfAbsent(key, k -> new ArrayList<>()).add(obj);
        return versionId;
    }

    /** GC sweep for chunks left behind by failed PUTs. Returns bytes freed. */
    public int collectOrphanChunks() {
        int freed = chunkStore.free(orphanChunkIds);
        orphanChunkIds.clear();
        return freed;
    }

    // --- read path (v2 item 2: verified against chunk checksums) ---

    private byte[] readChunks(ObjectMetadata obj) {
        byte[] out = new byte[obj.size];
        int offset = 0;
        for (String chunkId : obj.chunkIds) {
            byte[] chunk = chunkStore.get(chunkId);
            System.arraycopy(chunk, 0, out, offset, chunk.length);
            offset += chunk.length;
        }
        return out;
    }

    public byte[] getObject(String bucketName, String key, String versionId) {
        return getObjectWithRange(bucketName, key, versionId, -1, -1);
    }

    public byte[] getObjectWithRange(String bucketName, String key, String versionId, int start, int end) {
        if (!buckets.containsKey(bucketName)) {
            throw new IllegalArgumentException("Bucket not found");
        }

        Bucket bucket = buckets.get(bucketName);
        List<ObjectMetadata> versions = bucket.objects.get(key);
        if (versions == null || versions.isEmpty()) {
            throw new IllegalArgumentException("Object not found");
        }

        ObjectMetadata obj = null;
        if (versionId == null) {
            obj = versions.get(versions.size() - 1);
        } else {
            for (ObjectMetadata v : versions) {
                if (v.versionId.equals(versionId)) {
                    obj = v;
                    break;
                }
            }
        }

        if (obj == null || obj.isDeleted) {
            throw new IllegalArgumentException("Object not found or deleted");
        }

        byte[] data = readChunks(obj);
        if (start < 0 && end < 0) {
            return data;
        }

        int dataLen = data.length;
        int s = Math.max(0, start);
        int e = end < 0 ? dataLen - 1 : Math.min(dataLen - 1, end);

        if (s > e || s >= dataLen) {
            throw new IllegalArgumentException("Invalid byte range");
        }

        return Arrays.copyOfRange(data, s, e + 1);
    }

    // --- deletes (parity with v1) ---

    public String deleteObject(String bucketName, String key) {
        if (!buckets.containsKey(bucketName)) {
            throw new IllegalArgumentException("Bucket not found");
        }

        Bucket bucket = buckets.get(bucketName);
        String deleteVersionId = generateVersionId();
        ObjectMetadata deleteMarker = new ObjectMetadata(key, deleteVersionId, null, 0, true, null);
        bucket.objects.computeIfAbsent(key, k -> new ArrayList<>()).add(deleteMarker);
        return deleteVersionId;
    }

    public String deleteObject(String bucketName, String key, String versionId) {
        if (!buckets.containsKey(bucketName)) {
            throw new IllegalArgumentException("Bucket not found");
        }

        Bucket bucket = buckets.get(bucketName);
        List<ObjectMetadata> versions = bucket.objects.get(key);
        if (versions != null) {
            versions.removeIf(v -> v.versionId.equals(versionId));
            if (versions.isEmpty()) {
                bucket.objects.remove(key);
            }
        }
        return versionId;
    }

    // --- internal hook for multipart completion (parity with v1) ---

    public void putObjectInternal(String bucketName, String key, byte[] data, String etag) {
        if (!buckets.containsKey(bucketName)) {
            throw new IllegalArgumentException("Bucket not found");
        }
        commitObject(bucketName, key, data, etag);
    }

    // --- scrubber (v2 item 2) ---

    /** Run one scrubber pass over the chunk store; returns repairs made. */
    public int scrub() {
        return chunkStore.scrub();
    }

    /** Test/debug helper: physical chunk ids backing an object version. */
    public List<String> chunkIdsFor(String bucketName, String key, String versionId) {
        List<ObjectMetadata> versions = buckets.get(bucketName).objects.get(key);
        if (versionId == null) {
            return new ArrayList<>(versions.get(versions.size() - 1).chunkIds);
        }
        for (ObjectMetadata v : versions) {
            if (v.versionId.equals(versionId)) {
                return new ArrayList<>(v.chunkIds);
            }
        }
        throw new IllegalArgumentException("Version not found");
    }

    // --- presigned URLs (parity with v1) ---

    public String generatePresignedUrl(String bucketName, String key, String httpMethod, long expiryMillis) {
        // Note: This is an educational implementation and is not AWS SigV4 compatible.
        // It does not provide a production security guarantee.
        String basePath = "https://" + bucketName + ".s3.amazonaws.com/" + key;
        String canonicalRequest = httpMethod + "\n" + basePath + "\n" + expiryMillis;
        String signature = generateSignature(canonicalRequest, secretAccessKey);

        return basePath + "?expires=" + expiryMillis + "&signature=" + signature;
    }

    public boolean verifyPresignedUrl(String url, String httpMethod, long currentTimeMillis) {
        // Note: This is an educational implementation and is not AWS SigV4 compatible.
        // It does not provide a production security guarantee.
        try {
            if (!url.contains("?")) {
                return false;
            }

            String[] parts = url.split("\\?", 2);
            String basePath = parts[0];
            Map<String, String> params = new HashMap<>();
            for (String p : parts[1].split("&")) {
                String[] kv = p.split("=", 2);
                if (kv.length == 2) {
                    params.put(kv[0], kv[1]);
                }
            }

            long expires = Long.parseLong(params.getOrDefault("expires", "0"));
            String signature = params.get("signature");

            if (signature == null || expires == 0) {
                return false;
            }

            if (currentTimeMillis > expires) {
                return false;
            }

            if (usedSignatures.contains(signature)) {
                return false; // Replay attack
            }

            String canonicalRequest = httpMethod + "\n" + basePath + "\n" + expires;
            String expectedSignature = generateSignature(canonicalRequest, secretAccessKey);

            boolean isValid = MessageDigest.isEqual(
                expectedSignature.getBytes(StandardCharsets.UTF_8),
                signature.getBytes(StandardCharsets.UTF_8));
            if (isValid) {
                usedSignatures.add(signature);
            }
            return isValid;
        } catch (Exception e) {
            return false;
        }
    }

    static String md5Hex(byte[] data) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(data);
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private static String generateSignature(String data, byte[] secret) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret, "HmacSHA256"));
            byte[] raw = mac.doFinal(data.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : raw) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
