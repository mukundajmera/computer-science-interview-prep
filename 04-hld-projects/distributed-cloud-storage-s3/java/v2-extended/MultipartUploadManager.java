package v2_extended;

/**
 * v2-extended multipart upload manager.
 *
 * Improvement over v1-basic (named per the repo rule v1-basic -> v2-extended):
 * 3. Multipart lifecycle expiry (FOLLOW-UPS #2): an abandoned multipart
 *    upload leaks its uploaded parts forever. v2 stamps every upload with a
 *    creation time from an injectable clock and adds a configurable TTL plus
 *    sweepExpiredUploads(), the simulation of the background GC daemon that
 *    reclaims uploads older than the threshold and reports the bytes freed.
 *
 * Items 1 (chunks-before-metadata) and 2 (integrity + scrubber) live in
 * S3StorageService; completion goes through that service's chunks-first
 * commit path, so assembled objects get the same guarantees.
 */

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.LongSupplier;

public class MultipartUploadManager {

    public static class Part {
        public final int partNumber;
        public final byte[] data;
        public final String etag;

        public Part(int partNumber, byte[] data, String etag) {
            this.partNumber = partNumber;
            this.data = data;
            this.etag = etag;
        }
    }

    public static class MultipartUpload {
        public final String uploadId;
        public final String bucketName;
        public final String key;
        public final long createdAtMillis;
        public final Map<Integer, Part> parts = new HashMap<>();

        public MultipartUpload(String uploadId, String bucketName, String key, long createdAtMillis) {
            this.uploadId = uploadId;
            this.bucketName = bucketName;
            this.key = key;
            this.createdAtMillis = createdAtMillis;
        }

        public int storedBytes() {
            int total = 0;
            for (Part p : parts.values()) {
                total += p.data.length;
            }
            return total;
        }
    }

    public static class CompletedPart {
        public final int partNumber;
        public final String etag;

        public CompletedPart(int partNumber, String etag) {
            this.partNumber = partNumber;
            this.etag = etag;
        }
    }

    public static class SweepResult {
        public final List<String> expiredUploadIds;
        public final int bytesFreed;

        public SweepResult(List<String> expiredUploadIds, int bytesFreed) {
            this.expiredUploadIds = expiredUploadIds;
            this.bytesFreed = bytesFreed;
        }
    }

    private final S3StorageService storageService;
    private final Long uploadTtlMillis;
    private final LongSupplier clockMillis;
    public final Map<String, MultipartUpload> uploads = new HashMap<>();

    public MultipartUploadManager(S3StorageService storageService) {
        this(storageService, null, System::currentTimeMillis);
    }

    public MultipartUploadManager(S3StorageService storageService, Long uploadTtlMillis, LongSupplier clockMillis) {
        if (uploadTtlMillis != null && uploadTtlMillis <= 0) {
            throw new IllegalArgumentException("uploadTtlMillis must be positive or null");
        }
        if (clockMillis == null) {
            throw new IllegalArgumentException("clockMillis must not be null");
        }
        this.storageService = storageService;
        this.uploadTtlMillis = uploadTtlMillis;
        this.clockMillis = clockMillis;
    }

    public String initiateMultipartUpload(String bucketName, String key) {
        String uploadId = UUID.randomUUID().toString();
        uploads.put(uploadId, new MultipartUpload(uploadId, bucketName, key, clockMillis.getAsLong()));
        return uploadId;
    }

    public String uploadPart(String uploadId, int partNumber, byte[] data) {
        MultipartUpload upload = liveUpload(uploadId);
        if (partNumber < 1 || partNumber > 10000) {
            throw new IllegalArgumentException("Invalid part number");
        }

        String etag = S3StorageService.md5Hex(data);
        upload.parts.put(partNumber, new Part(partNumber, data, etag));

        return etag;
    }

    public String completeMultipartUpload(String uploadId, List<CompletedPart> partsToComplete) {
        MultipartUpload upload = liveUpload(uploadId);

        int previousPartNumber = 0;
        int totalSize = 0;
        List<Part> orderedParts = new ArrayList<>();

        for (CompletedPart completedPart : partsToComplete) {
            int partNumber = completedPart.partNumber;
            if (partNumber <= previousPartNumber) {
                throw new IllegalArgumentException("Part numbers must be in ascending order");
            }

            Part part = upload.parts.get(partNumber);
            if (part == null) {
                throw new IllegalArgumentException("Part number " + partNumber + " not found");
            }
            if (!part.etag.equals(completedPart.etag)) {
                throw new IllegalArgumentException("Invalid ETag for part " + partNumber);
            }

            previousPartNumber = partNumber;
            totalSize += part.data.length;
            orderedParts.add(part);
        }

        byte[] finalObjectData = new byte[totalSize];
        StringBuilder combinedEtagHex = new StringBuilder();

        int offset = 0;
        for (Part p : orderedParts) {
            System.arraycopy(p.data, 0, finalObjectData, offset, p.data.length);
            offset += p.data.length;
            combinedEtagHex.append(p.etag);
        }

        String compositeEtagRaw = S3StorageService.md5Hex(hexToBytes(combinedEtagHex.toString()));
        String compositeEtag = compositeEtagRaw + "-" + orderedParts.size();

        storageService.putObjectInternal(upload.bucketName, upload.key, finalObjectData, compositeEtag);

        uploads.remove(uploadId);

        return compositeEtag;
    }

    public void abortMultipartUpload(String uploadId) {
        if (!uploads.containsKey(uploadId)) {
            throw new IllegalArgumentException("Upload ID not found");
        }
        uploads.remove(uploadId);
    }

    /** GC daemon pass (v2 item 3): remove uploads older than the TTL and
     * reclaim their part data. With no TTL configured, nothing expires
     * (v1 parity). */
    public SweepResult sweepExpiredUploads() {
        if (uploadTtlMillis == null) {
            return new SweepResult(new ArrayList<>(), 0);
        }
        long now = clockMillis.getAsLong();
        List<String> expired = new ArrayList<>();
        for (Map.Entry<String, MultipartUpload> entry : uploads.entrySet()) {
            if (now - entry.getValue().createdAtMillis > uploadTtlMillis) {
                expired.add(entry.getKey());
            }
        }
        int freed = 0;
        for (String uploadId : expired) {
            freed += uploads.get(uploadId).storedBytes();
            uploads.remove(uploadId);
        }
        return new SweepResult(expired, freed);
    }

    private MultipartUpload liveUpload(String uploadId) {
        MultipartUpload upload = uploads.get(uploadId);
        if (upload == null) {
            throw new IllegalArgumentException("Upload ID not found");
        }
        if (uploadTtlMillis != null && clockMillis.getAsLong() - upload.createdAtMillis > uploadTtlMillis) {
            throw new IllegalArgumentException("Upload ID expired");
        }
        return upload;
    }

    private static byte[] hexToBytes(String hex) {
        byte[] out = new byte[hex.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(hex.substring(2 * i, 2 * i + 2), 16);
        }
        return out;
    }
}
