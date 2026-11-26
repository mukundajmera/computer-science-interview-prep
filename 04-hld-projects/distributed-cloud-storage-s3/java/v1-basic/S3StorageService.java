package v1_basic;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.util.stream.Collectors;

public class S3StorageService {
    // S3 requires strong read-after-write metadata consistency.
    // We'll simulate this with ConcurrentHashMap and Atomic types where applicable.
    
    private final Map<String, Bucket> buckets = new ConcurrentHashMap<>();
    private final String secretAccessKey = "test-secret-key"; // Normally fetched securely
    private final Set<String> usedSignatures = ConcurrentHashMap.newKeySet();

    static class Bucket {
        String name;
        Map<String, List<ObjectMetadata>> objects = new ConcurrentHashMap<>(); // key -> version history

        public Bucket(String name) {
            this.name = name;
        }
    }

    public static class ObjectMetadata {
        public String key;
        public String versionId;
        public byte[] data;
        public long size;
        public boolean isDeleted;
        public long lastModified;
        public String etag;

        public ObjectMetadata(String key, String versionId, byte[] data, boolean isDeleted, String etag) {
            this.key = key;
            this.versionId = versionId;
            this.data = data;
            this.size = data != null ? data.length : 0;
            this.isDeleted = isDeleted;
            this.lastModified = System.currentTimeMillis();
            this.etag = etag;
        }
    }

    public void createBucket(String bucketName) {
        buckets.putIfAbsent(bucketName, new Bucket(bucketName));
    }

    public void deleteBucket(String bucketName) {
        buckets.remove(bucketName);
    }

    private String generateVersionId() {
        return UUID.randomUUID().toString();
    }
    
    private String calculateMD5Etag(byte[] data) {
        if (data == null) return null;
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(data);
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 not supported", e);
        }
    }

    public String putObject(String bucketName, String key, byte[] data) {
        Bucket bucket = buckets.get(bucketName);
        if (bucket == null) throw new IllegalArgumentException("Bucket not found");

        String versionId = generateVersionId();
        String etag = calculateMD5Etag(data);
        ObjectMetadata obj = new ObjectMetadata(key, versionId, data, false, etag);

        bucket.objects.compute(key, (k, v) -> {
            if (v == null) v = new ArrayList<>();
            v.add(obj);
            return v;
        });

        return versionId;
    }

    public byte[] getObject(String bucketName, String key, String versionId) {
        return getObjectWithRange(bucketName, key, versionId, -1, -1);
    }

    public byte[] getObjectWithRange(String bucketName, String key, String versionId, int start, int end) {
        Bucket bucket = buckets.get(bucketName);
        if (bucket == null) throw new IllegalArgumentException("Bucket not found");

        List<ObjectMetadata> versions = bucket.objects.get(key);
        if (versions == null || versions.isEmpty()) throw new IllegalArgumentException("Object not found");

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

        if (obj == null || obj.isDeleted) throw new IllegalArgumentException("Object not found or deleted");

        if (start < 0 && end < 0) {
            return obj.data;
        }

        // Byte range request
        int len = obj.data.length;
        int s = Math.max(0, start);
        int e = end < 0 ? len - 1 : Math.min(len - 1, end);

        if (s > e || s >= len) {
            throw new IllegalArgumentException("Invalid byte range");
        }

        return Arrays.copyOfRange(obj.data, s, e + 1);
    }

    public String deleteObject(String bucketName, String key) {
        return deleteObject(bucketName, key, null);
    }
    
    public String deleteObject(String bucketName, String key, String versionId) {
        Bucket bucket = buckets.get(bucketName);
        if (bucket == null) throw new IllegalArgumentException("Bucket not found");

        if (versionId == null) {
            // Soft delete: creates a delete marker instead of removing a specific version
            String deleteVersionId = generateVersionId();
            ObjectMetadata deleteMarker = new ObjectMetadata(key, deleteVersionId, null, true, null);

            bucket.objects.compute(key, (k, v) -> {
                if (v == null) v = new ArrayList<>();
                v.add(deleteMarker);
                return v;
            });

            return deleteVersionId;
        } else {
            // Hard delete: removes the selected version from the bucket
            bucket.objects.computeIfPresent(key, (k, v) -> {
                v.removeIf(obj -> obj.versionId.equals(versionId));
                return v.isEmpty() ? null : v;
            });
            return versionId;
        }
    }
    
    // Internal use for testing multipart upload results
    public void putObjectInternal(String bucketName, String key, byte[] data, String etag) {
        Bucket bucket = buckets.get(bucketName);
        if (bucket == null) throw new IllegalArgumentException("Bucket not found");

        String versionId = generateVersionId();
        ObjectMetadata obj = new ObjectMetadata(key, versionId, data, false, etag);

        bucket.objects.compute(key, (k, v) -> {
            if (v == null) v = new ArrayList<>();
            v.add(obj);
            return v;
        });
    }

    public boolean verifyPresignedUrl(String url, String httpMethod, long currentTimeMillis) {
        // Note: This is an educational implementation and is not AWS SigV4 compatible. 
        // It does not provide a production security guarantee.
        try {
            int qMark = url.indexOf('?');
            if (qMark == -1) return false;
            
            String basePath = url.substring(0, qMark);
            String[] params = url.substring(qMark + 1).split("&");
            long expires = 0;
            String signature = null;
            
            for (String p : params) {
                String[] kv = p.split("=");
                if (kv.length != 2) continue;
                if (kv[0].equals("expires")) expires = Long.parseLong(kv[1]);
                if (kv[0].equals("signature")) signature = kv[1];
            }
            
            if (signature == null || expires == 0) return false;
            if (currentTimeMillis > expires) return false; // Expired
            if (usedSignatures.contains(signature)) return false; // Replay attack
            
            String canonicalRequest = httpMethod + "\n" + basePath + "\n" + expires;
            String expectedSignature = generateSignature(canonicalRequest, secretAccessKey);
            
            if (MessageDigest.isEqual(expectedSignature.getBytes(StandardCharsets.UTF_8), signature.getBytes(StandardCharsets.UTF_8))) {
                usedSignatures.add(signature);
                return true;
            }
            return false;
        } catch (Exception e) {
            return false;
        }
    }
    
    public String generatePresignedUrl(String bucketName, String key, String httpMethod, long expiryMillis) {
        // Note: This is an educational implementation and is not AWS SigV4 compatible. 
        // It does not provide a production security guarantee.
        String basePath = "https://" + bucketName + ".s3.amazonaws.com/" + key;
        String canonicalRequest = httpMethod + "\n" + basePath + "\n" + expiryMillis;
        String signature = generateSignature(canonicalRequest, secretAccessKey);
        
        return basePath + "?expires=" + expiryMillis + "&signature=" + signature;
    }

    private String generateSignature(String data, String secret) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            SecretKeySpec secretKeySpec = new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256");
            mac.init(secretKeySpec);
            byte[] hmac = mac.doFinal(data.getBytes(StandardCharsets.UTF_8));
            
            StringBuilder sb = new StringBuilder();
            for (byte b : hmac) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException("Failed to generate signature", e);
        }
    }
}
