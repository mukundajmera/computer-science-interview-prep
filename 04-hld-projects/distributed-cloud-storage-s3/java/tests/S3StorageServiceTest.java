import v1_basic.S3StorageService;
import v1_basic.MultipartUploadManager;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;

public class S3StorageServiceTest {
    public static void main(String[] args) {
        testBucketOperations();
        testByteRangeRequest();
        testSoftDeleteAndVersions();
        testVersionedDeletes();
        testMultipartUpload();
        testPresignedUrl();
        System.out.println("All Java tests passed!");
    }

    private static void assertEquals(Object expected, Object actual, String message) {
        if (expected == null && actual == null) return;
        if (expected != null && expected.equals(actual)) return;
        throw new AssertionError(message + " - Expected: " + expected + ", Actual: " + actual);
    }
    
    private static void assertArrayEquals(byte[] expected, byte[] actual, String message) {
        if (!Arrays.equals(expected, actual)) {
            throw new AssertionError(message + " - Arrays not equal");
        }
    }
    
    private static void assertTrue(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
    
    private static void assertFalse(boolean condition, String message) {
        if (condition) throw new AssertionError(message);
    }

    private static void assertNotNull(Object obj, String message) {
        if (obj == null) throw new AssertionError(message + " - Expected not null");
    }

    public static void testBucketOperations() {
        S3StorageService s3 = new S3StorageService();
        String bucket = "my-bucket";
        s3.createBucket(bucket);
        
        String key = "test.txt";
        byte[] data = "Hello, S3!".getBytes(StandardCharsets.UTF_8);
        
        String versionId = s3.putObject(bucket, key, data);
        assertNotNull(versionId, "versionId should not be null");
        
        byte[] retrieved = s3.getObject(bucket, key, versionId);
        assertArrayEquals(data, retrieved, "retrieved data should match");
        
        s3.deleteBucket(bucket);
        try {
            s3.getObject(bucket, key, versionId);
            throw new AssertionError("Should throw IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            // Expected
        }
    }

    public static void testByteRangeRequest() {
        S3StorageService s3 = new S3StorageService();
        String bucket = "range-bucket";
        s3.createBucket(bucket);
        
        String key = "data.bin";
        byte[] data = new byte[]{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
        
        String versionId = s3.putObject(bucket, key, data);
        
        byte[] retrieved = s3.getObjectWithRange(bucket, key, versionId, 2, 5);
        assertArrayEquals(new byte[]{2, 3, 4, 5}, retrieved, "Range 2-5");
        
        byte[] retrievedEnd = s3.getObjectWithRange(bucket, key, versionId, 7, -1);
        assertArrayEquals(new byte[]{7, 8, 9}, retrievedEnd, "Range 7 to end");
        
        try {
            s3.getObjectWithRange(bucket, key, versionId, 10, 12);
            throw new AssertionError("Should throw IllegalArgumentException for start >= len");
        } catch (IllegalArgumentException e) {
            // Expected
        }

        try {
            s3.getObjectWithRange(bucket, key, versionId, 5, 2);
            throw new AssertionError("Should throw IllegalArgumentException for start > end");
        } catch (IllegalArgumentException e) {
            // Expected
        }
    }

    public static void testSoftDeleteAndVersions() {
        S3StorageService s3 = new S3StorageService();
        String bucket = "version-bucket";
        s3.createBucket(bucket);
        
        String key = "doc.txt";
        byte[] data1 = "V1".getBytes(StandardCharsets.UTF_8);
        byte[] data2 = "V2".getBytes(StandardCharsets.UTF_8);
        
        String v1 = s3.putObject(bucket, key, data1);
        String v2 = s3.putObject(bucket, key, data2);
        
        assertArrayEquals(data1, s3.getObject(bucket, key, v1), "Get V1");
        assertArrayEquals(data2, s3.getObject(bucket, key, v2), "Get V2");
        assertArrayEquals(data2, s3.getObject(bucket, key, null), "Get latest");
        
        // Deleting without version creates a marker
        s3.deleteObject(bucket, key);
        
        try {
            s3.getObject(bucket, key, null);
            throw new AssertionError("Should throw IllegalArgumentException after soft delete");
        } catch (IllegalArgumentException e) {
            // Expected
        }
        
        assertArrayEquals(data1, s3.getObject(bucket, key, v1), "V1 still accessible");
    }

    public static void testVersionedDeletes() {
        S3StorageService s3 = new S3StorageService();
        String bucket = "delete-version-bucket";
        s3.createBucket(bucket);
        String key = "file.txt";
        
        byte[] data1 = "V1".getBytes(StandardCharsets.UTF_8);
        byte[] data2 = "V2".getBytes(StandardCharsets.UTF_8);
        
        String v1 = s3.putObject(bucket, key, data1);
        String v2 = s3.putObject(bucket, key, data2);
        
        // Deleting a specific version removes it completely
        s3.deleteObject(bucket, key, v1);
        try {
            s3.getObject(bucket, key, v1);
            throw new AssertionError("Should throw IllegalArgumentException for deleted version");
        } catch (IllegalArgumentException e) {
            // Expected
        }
        
        // V2 is still accessible
        assertArrayEquals(data2, s3.getObject(bucket, key, v2), "V2 still accessible");
    }

    public static void testMultipartUpload() {
        S3StorageService s3 = new S3StorageService();
        MultipartUploadManager multipart = new MultipartUploadManager(s3);
        String bucket = "mp-bucket";
        s3.createBucket(bucket);
        String key = "large.bin";
        
        String uploadId = multipart.initiateMultipartUpload(bucket, key);
        
        byte[] part1 = "Part 1 Data ".getBytes(StandardCharsets.UTF_8);
        byte[] part2 = "Part 2 Data".getBytes(StandardCharsets.UTF_8);
        
        String etag1 = multipart.uploadPart(uploadId, 1, part1);
        String etag2 = multipart.uploadPart(uploadId, 2, part2);
        
        String compositeEtag = multipart.completeMultipartUpload(uploadId, Arrays.asList(
            new MultipartUploadManager.CompletedPart(1, etag1),
            new MultipartUploadManager.CompletedPart(2, etag2)
        ));
        assertTrue(compositeEtag.endsWith("-2"), "ETag ends with -2");
        
        // Replayed complete
        try {
            multipart.completeMultipartUpload(uploadId, Arrays.asList(
                new MultipartUploadManager.CompletedPart(1, etag1),
                new MultipartUploadManager.CompletedPart(2, etag2)
            ));
            throw new AssertionError("Should throw IllegalArgumentException for replayed complete");
        } catch (IllegalArgumentException e) {
            // Expected
        }
        
        byte[] combined = s3.getObject(bucket, key, null);
        String expectedCombined = "Part 1 Data Part 2 Data";
        assertEquals(expectedCombined, new String(combined, StandardCharsets.UTF_8), "Combined parts");
        
        String uploadId2 = multipart.initiateMultipartUpload(bucket, "other.bin");
        String etag2_1 = multipart.uploadPart(uploadId2, 1, part1);
        String etag2_2 = multipart.uploadPart(uploadId2, 2, part2);
        
        // Out of order parts
        try {
            multipart.completeMultipartUpload(uploadId2, Arrays.asList(
                new MultipartUploadManager.CompletedPart(2, etag2_2),
                new MultipartUploadManager.CompletedPart(1, etag2_1)
            ));
            throw new AssertionError("Should throw IllegalArgumentException for out of order parts");
        } catch (IllegalArgumentException e) {
            // Expected
        }

        // Duplicate parts
        try {
            multipart.completeMultipartUpload(uploadId2, Arrays.asList(
                new MultipartUploadManager.CompletedPart(1, etag2_1),
                new MultipartUploadManager.CompletedPart(1, etag2_1)
            ));
            throw new AssertionError("Should throw IllegalArgumentException for duplicate parts");
        } catch (IllegalArgumentException e) {
            // Expected
        }

        // Missing parts
        try {
            multipart.completeMultipartUpload(uploadId2, Arrays.asList(
                new MultipartUploadManager.CompletedPart(3, "fake-etag")
            ));
            throw new AssertionError("Should throw IllegalArgumentException for missing parts");
        } catch (IllegalArgumentException e) {
            // Expected
        }

        // Checksum mismatch
        try {
            multipart.completeMultipartUpload(uploadId2, Arrays.asList(
                new MultipartUploadManager.CompletedPart(1, "bad-etag")
            ));
            throw new AssertionError("Should throw IllegalArgumentException for checksum mismatch");
        } catch (IllegalArgumentException e) {
            // Expected
        }

        // Abort upload
        multipart.abortMultipartUpload(uploadId2);
        
        // Replayed abort
        try {
            multipart.abortMultipartUpload(uploadId2);
            throw new AssertionError("Should throw IllegalArgumentException for aborting already aborted upload");
        } catch (IllegalArgumentException e) {
            // Expected
        }
        
        // Ensure no metadata was published for aborted upload
        try {
            s3.getObject(bucket, "other.bin", null);
            throw new AssertionError("Should throw IllegalArgumentException as object was never published");
        } catch (IllegalArgumentException e) {
            // Expected
        }
    }

    public static void testPresignedUrl() {
        S3StorageService s3 = new S3StorageService();
        String bucket = "auth-bucket";
        String key = "private.png";
        
        long now = System.currentTimeMillis();
        long expiry = now + 3600_000;
        
        String url = s3.generatePresignedUrl(bucket, key, "GET", expiry);
        assertTrue(url.contains("expires=" + expiry), "URL contains expiry");
        
        assertFalse(s3.verifyPresignedUrl(url, "GET", expiry + 1000), "Expired URL");
        assertFalse(s3.verifyPresignedUrl(url, "PUT", now), "Altered method");
        
        String tamperedUrl = url.replace("expires=" + expiry, "expires=" + (expiry + 10000));
        assertFalse(s3.verifyPresignedUrl(tamperedUrl, "GET", now), "Altered expiry parameter");
        
        String tamperedPathUrl = url.replace("private.png", "public.png");
        assertFalse(s3.verifyPresignedUrl(tamperedPathUrl, "GET", now), "Altered path parameter");
        
        // Final assertions - register the valid URL, then test replay
        assertTrue(s3.verifyPresignedUrl(url, "GET", now), "Valid URL");
        assertFalse(s3.verifyPresignedUrl(url, "GET", now), "Replay attack should fail");
    }
}
