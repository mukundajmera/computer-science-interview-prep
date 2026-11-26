package v1_basic;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

public class MultipartUploadManager {
    private final S3StorageService storageService;
    private final Map<String, MultipartUpload> uploads = new ConcurrentHashMap<>();

    public MultipartUploadManager(S3StorageService storageService) {
        this.storageService = storageService;
    }

    public static class MultipartUpload {
        public String uploadId;
        public String bucketName;
        public String key;
        public Map<Integer, Part> parts = new ConcurrentHashMap<>();

        public MultipartUpload(String uploadId, String bucketName, String key) {
            this.uploadId = uploadId;
            this.bucketName = bucketName;
            this.key = key;
        }
    }

    public static class Part {
        public int partNumber;
        public byte[] data;
        public String etag;

        public Part(int partNumber, byte[] data, String etag) {
            this.partNumber = partNumber;
            this.data = data;
            this.etag = etag;
        }
    }

    public static class CompletedPart {
        public int partNumber;
        public String etag;

        public CompletedPart(int partNumber, String etag) {
            this.partNumber = partNumber;
            this.etag = etag;
        }
    }

    public String initiateMultipartUpload(String bucketName, String key) {
        String uploadId = UUID.randomUUID().toString();
        uploads.put(uploadId, new MultipartUpload(uploadId, bucketName, key));
        return uploadId;
    }

    public String uploadPart(String uploadId, int partNumber, byte[] data) {
        MultipartUpload upload = uploads.get(uploadId);
        if (upload == null) throw new IllegalArgumentException("Upload ID not found");
        if (partNumber < 1 || partNumber > 10000) throw new IllegalArgumentException("Invalid part number");

        String etag = calculateMD5Etag(data);
        upload.parts.put(partNumber, new Part(partNumber, data, etag));
        return etag;
    }

    public String completeMultipartUpload(String uploadId, List<CompletedPart> partsToComplete) {
        MultipartUpload upload = uploads.get(uploadId);
        if (upload == null) throw new IllegalArgumentException("Upload ID not found");

        // Validate parts in ascending order
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
            
            // For composite Etag we append the raw bytes of the individual part ETags?
            // Actually AWS standard is MD5(MD5(part1) + MD5(part2) + ... ) + "-" + numParts
            // Let's concatenate hex strings or bytes. We will concatenate the raw bytes of the ETags.
            orderedParts.add(part);
        }

        // Concatenate chunks
        byte[] finalObjectData = new byte[totalSize];
        int offset = 0;
        byte[] combinedEtagBytes = new byte[orderedParts.size() * 16]; // each md5 is 16 bytes
        
        try {
            MessageDigest md5 = MessageDigest.getInstance("MD5");
            int etagOffset = 0;
            for (Part p : orderedParts) {
                System.arraycopy(p.data, 0, finalObjectData, offset, p.data.length);
                offset += p.data.length;
                
                // Decode hex etag to bytes
                byte[] etagBytes = hexStringToByteArray(p.etag);
                System.arraycopy(etagBytes, 0, combinedEtagBytes, etagOffset, etagBytes.length);
                etagOffset += etagBytes.length;
            }
            
            // Produce composite ETag
            byte[] compositeEtagRaw = md5.digest(combinedEtagBytes);
            String compositeEtag = byteArrayToHexString(compositeEtagRaw) + "-" + orderedParts.size();
            
            // Save final object to S3
            storageService.putObjectInternal(upload.bucketName, upload.key, finalObjectData, compositeEtag);
            
            // Clean up
            uploads.remove(uploadId);
            
            return compositeEtag;

        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    public void abortMultipartUpload(String uploadId) {
        MultipartUpload upload = uploads.remove(uploadId);
        if (upload == null) throw new IllegalArgumentException("Upload ID not found");
    }

    private String calculateMD5Etag(byte[] data) {
        if (data == null) return null;
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(data);
            return byteArrayToHexString(digest);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 not supported", e);
        }
    }
    
    private String byteArrayToHexString(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
    
    private byte[] hexStringToByteArray(String s) {
        int len = s.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4)
                                 + Character.digit(s.charAt(i+1), 16));
        }
        return data;
    }
}
