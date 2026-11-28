import v2_extended.S3StorageService;
import v2_extended.S3StorageService.ChunkStore;
import v2_extended.S3StorageService.ChunkIntegrityError;
import v2_extended.S3StorageService.InjectedWriteError;
import v2_extended.MultipartUploadManager;
import v2_extended.MultipartUploadManager.CompletedPart;
import v2_extended.MultipartUploadManager.SweepResult;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.List;

public class S3StorageServiceV2Test {

    private static S3StorageService service;
    private static ChunkStore chunkStore;
    private static MultipartUploadManager mpManager;

    public static void main(String[] args) {
        // Parity tests: v2 must keep every v1 guarantee
        testBucketOperations();
        testByteRangeRequest();
        testSoftDeleteAndVersions();
        testVersionedDeletes();
        testMultipartUpload();
        testPresignedUrl();
        // v2 item 1: data chunks before metadata, with failure injection
        testFailedChunkWriteCommitsNoMetadata();
        testFailedChunkWriteLeavesTrackedOrphans();
        testSuccessfulPutCreatesNoOrphans();
        testObjectSpansMultipleChunks();
        // v2 item 2: integrity checking and scrubber
        testCorruptedChunkRaisesIntegrityError();
        testScrubRepairsCorruptedChunk();
        testScrubOnCleanStoreRepairsNothing();
        // v2 item 3: multipart lifecycle expiry
        testExpiredUploadIsRejectedAndSwept();
        testFreshUploadSurvivesSweep();
        testNoTtlMeansNoExpiry();
        testCompletedUploadIsNotSwept();
        System.out.println("All Java v2 tests passed!");
    }

    private static void reset() {
        chunkStore = new ChunkStore();
        service = new S3StorageService(chunkStore, S3StorageService.DEFAULT_CHUNK_SIZE);
        mpManager = new MultipartUploadManager(service);
    }

    // --- Parity tests ---

    private static void testBucketOperations() {
        reset();
        service.createBucket("test-bucket");
        byte[] data = "Hello, S3!".getBytes(StandardCharsets.UTF_8);
        String versionId = service.putObject("test-bucket", "test.txt", data);
        assertTrue(versionId != null && !versionId.isEmpty(), "version id returned");
        assertArrayEquals(data, service.getObject("test-bucket", "test.txt", versionId), "roundtrip");
        service.deleteBucket("test-bucket");
        expectThrows(() -> service.getObject("test-bucket", "test.txt", versionId), "get after bucket delete");
    }

    private static void testByteRangeRequest() {
        reset();
        service.createBucket("range-bucket");
        byte[] data = new byte[]{0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
        String versionId = service.putObject("range-bucket", "data.bin", data);
        assertArrayEquals(new byte[]{2, 3, 4, 5},
            service.getObjectWithRange("range-bucket", "data.bin", versionId, 2, 5), "range 2-5");
        assertArrayEquals(new byte[]{7, 8, 9},
            service.getObjectWithRange("range-bucket", "data.bin", versionId, 7, -1), "range 7-end");
        expectThrows(() -> service.getObjectWithRange("range-bucket", "data.bin", versionId, 10, 12), "out of bounds");
        expectThrows(() -> service.getObjectWithRange("range-bucket", "data.bin", versionId, 5, 2), "reversed range");
    }

    private static void testSoftDeleteAndVersions() {
        reset();
        service.createBucket("version-bucket");
        String v1 = service.putObject("version-bucket", "doc.txt", new byte[]{1});
        String v2 = service.putObject("version-bucket", "doc.txt", new byte[]{2});
        assertArrayEquals(new byte[]{1}, service.getObject("version-bucket", "doc.txt", v1), "v1 readable");
        assertArrayEquals(new byte[]{2}, service.getObject("version-bucket", "doc.txt", v2), "v2 readable");
        assertArrayEquals(new byte[]{2}, service.getObject("version-bucket", "doc.txt", null), "latest is v2");
        service.deleteObject("version-bucket", "doc.txt");
        expectThrows(() -> service.getObject("version-bucket", "doc.txt", null), "latest is delete marker");
        assertArrayEquals(new byte[]{1}, service.getObject("version-bucket", "doc.txt", v1), "v1 survives soft delete");
    }

    private static void testVersionedDeletes() {
        reset();
        service.createBucket("delete-version-bucket");
        String v1 = service.putObject("delete-version-bucket", "file.txt", new byte[]{1});
        String v2 = service.putObject("delete-version-bucket", "file.txt", new byte[]{2});
        service.deleteObject("delete-version-bucket", "file.txt", v1);
        expectThrows(() -> service.getObject("delete-version-bucket", "file.txt", v1), "hard-deleted v1 gone");
        assertArrayEquals(new byte[]{2}, service.getObject("delete-version-bucket", "file.txt", v2), "v2 intact");
    }

    private static void testMultipartUpload() {
        reset();
        service.createBucket("mp-bucket");
        String uploadId = mpManager.initiateMultipartUpload("mp-bucket", "large.bin");
        byte[] part1 = "Part 1 Data ".getBytes(StandardCharsets.UTF_8);
        byte[] part2 = "Part 2 Data".getBytes(StandardCharsets.UTF_8);
        String etag1 = mpManager.uploadPart(uploadId, 1, part1);
        String etag2 = mpManager.uploadPart(uploadId, 2, part2);
        String composite = mpManager.completeMultipartUpload(uploadId,
            Arrays.asList(new CompletedPart(1, etag1), new CompletedPart(2, etag2)));
        assertTrue(composite.endsWith("-2"), "composite etag carries part count");
        expectThrows(() -> mpManager.completeMultipartUpload(uploadId,
            Arrays.asList(new CompletedPart(1, etag1), new CompletedPart(2, etag2))), "replayed complete");
        assertArrayEquals("Part 1 Data Part 2 Data".getBytes(StandardCharsets.UTF_8),
            service.getObject("mp-bucket", "large.bin", null), "assembled object");

        String uploadId2 = mpManager.initiateMultipartUpload("mp-bucket", "other.bin");
        String e1 = mpManager.uploadPart(uploadId2, 1, part1);
        String e2 = mpManager.uploadPart(uploadId2, 2, part2);
        expectThrows(() -> mpManager.completeMultipartUpload(uploadId2,
            Arrays.asList(new CompletedPart(2, e2), new CompletedPart(1, e1))), "out of order");
        expectThrows(() -> mpManager.completeMultipartUpload(uploadId2,
            Arrays.asList(new CompletedPart(1, e1), new CompletedPart(1, e1))), "duplicate parts");
        expectThrows(() -> mpManager.completeMultipartUpload(uploadId2,
            List.of(new CompletedPart(3, "fake-etag"))), "missing part");
        expectThrows(() -> mpManager.completeMultipartUpload(uploadId2,
            List.of(new CompletedPart(1, "bad-etag"))), "etag mismatch");
        mpManager.abortMultipartUpload(uploadId2);
        expectThrows(() -> mpManager.abortMultipartUpload(uploadId2), "replayed abort");
        expectThrows(() -> service.getObject("mp-bucket", "other.bin", null), "aborted upload published nothing");
    }

    private static void testPresignedUrl() {
        reset();
        long now = System.currentTimeMillis();
        long expiry = now + 3_600_000L;
        String url = service.generatePresignedUrl("auth-bucket", "private.png", "GET", expiry);
        assertTrue(url.contains("expires=" + expiry), "url carries expiry");
        assertTrue(!service.verifyPresignedUrl(url, "GET", expiry + 1000), "expired rejected");
        assertTrue(!service.verifyPresignedUrl(url, "PUT", now), "wrong method rejected");
        String tampered = url.replace("expires=" + expiry, "expires=" + (expiry + 10000));
        assertTrue(!service.verifyPresignedUrl(tampered, "GET", now), "tampered expiry rejected");
        String tamperedPath = url.replace("private.png", "public.png");
        assertTrue(!service.verifyPresignedUrl(tamperedPath, "GET", now), "tampered path rejected");
        assertTrue(service.verifyPresignedUrl(url, "GET", now), "valid url accepted");
        assertTrue(!service.verifyPresignedUrl(url, "GET", now), "replay rejected");
    }

    // --- v2 item 1 ---

    private static void testFailedChunkWriteCommitsNoMetadata() {
        reset();
        service.createBucket("fail-bucket");
        byte[] data = "0123456789ABCDEF0123456789ABCDEF".getBytes(StandardCharsets.UTF_8);
        chunkStore.injectWriteFailures(1, 1); // second chunk write fails
        expectThrows(InjectedWriteError.class,
            () -> service.putObject("fail-bucket", "obj.bin", data), "injected failure surfaces");
        expectThrows(() -> service.getObject("fail-bucket", "obj.bin", null), "no dangling metadata");
    }

    private static void testFailedChunkWriteLeavesTrackedOrphans() {
        reset();
        service.createBucket("orphan-bucket");
        byte[] data = "0123456789ABCDEF0123456789ABCDEF".getBytes(StandardCharsets.UTF_8);
        chunkStore.injectWriteFailures(1, 1); // first chunk lands, second fails
        expectThrows(InjectedWriteError.class,
            () -> service.putObject("orphan-bucket", "obj.bin", data), "injected failure surfaces");
        assertEquals(1, service.orphanChunkIds.size(), "one orphan tracked");
        assertEquals(16, service.collectOrphanChunks(), "orphan bytes freed");
        assertEquals(0, chunkStore.chunks.size(), "store empty after GC");
    }

    private static void testSuccessfulPutCreatesNoOrphans() {
        reset();
        service.createBucket("clean-bucket");
        service.putObject("clean-bucket", "obj.bin",
            "0123456789ABCDEF0123456789ABCDEF".getBytes(StandardCharsets.UTF_8));
        assertEquals(0, service.orphanChunkIds.size(), "no orphans on success");
        assertEquals(0, service.collectOrphanChunks(), "nothing to free");
    }

    private static void testObjectSpansMultipleChunks() {
        reset();
        service.createBucket("multi-chunk-bucket");
        byte[] data = new byte[64];
        for (int i = 0; i < 64; i++) data[i] = (byte) i;
        String versionId = service.putObject("multi-chunk-bucket", "wide.bin", data);
        assertEquals(4, service.chunkIdsFor("multi-chunk-bucket", "wide.bin", versionId).size(), "4 chunks");
        assertArrayEquals(new byte[]{14, 15, 16, 17, 18},
            service.getObjectWithRange("multi-chunk-bucket", "wide.bin", versionId, 14, 18),
            "range across chunk boundary");
    }

    // --- v2 item 2 ---

    private static void testCorruptedChunkRaisesIntegrityError() {
        reset();
        service.createBucket("bitrot-bucket");
        service.putObject("bitrot-bucket", "obj.bin", "0123456789ABCDEF".getBytes(StandardCharsets.UTF_8));
        String chunkId = service.chunkIdsFor("bitrot-bucket", "obj.bin", null).get(0);
        chunkStore.corrupt(chunkId);
        expectThrows(ChunkIntegrityError.class,
            () -> service.getObject("bitrot-bucket", "obj.bin", null), "integrity error raised");
    }

    private static void testScrubRepairsCorruptedChunk() {
        reset();
        service.createBucket("scrub-bucket");
        byte[] data = "0123456789ABCDEF".getBytes(StandardCharsets.UTF_8);
        service.putObject("scrub-bucket", "obj.bin", data);
        String chunkId = service.chunkIdsFor("scrub-bucket", "obj.bin", null).get(0);
        chunkStore.corrupt(chunkId);
        assertEquals(1, service.scrub(), "one chunk repaired");
        assertArrayEquals(data, service.getObject("scrub-bucket", "obj.bin", null), "readable after scrub");
    }

    private static void testScrubOnCleanStoreRepairsNothing() {
        reset();
        service.createBucket("healthy-bucket");
        service.putObject("healthy-bucket", "obj.bin",
            "0123456789ABCDEF0123456789ABCDEF".getBytes(StandardCharsets.UTF_8));
        assertEquals(0, service.scrub(), "clean store needs no repairs");
    }

    // --- v2 item 3 ---

    private static class FakeClock {
        long now;
        FakeClock(long start) { this.now = start; }
        long get() { return now; }
        void advance(long millis) { now += millis; }
    }

    private static void testExpiredUploadIsRejectedAndSwept() {
        reset();
        FakeClock clock = new FakeClock(1_000_000L);
        MultipartUploadManager manager = new MultipartUploadManager(service, 60_000L, clock::get);
        service.createBucket("ttl-bucket");
        String uploadId = manager.initiateMultipartUpload("ttl-bucket", "big.bin");
        manager.uploadPart(uploadId, 1, "0123456789ABCDEF".getBytes(StandardCharsets.UTF_8));
        clock.advance(61_000L);
        expectThrows(() -> manager.uploadPart(uploadId, 2, new byte[]{1}), "expired upload rejects parts");
        SweepResult result = manager.sweepExpiredUploads();
        assertEquals(1, result.expiredUploadIds.size(), "one upload expired");
        assertEquals(uploadId, result.expiredUploadIds.get(0), "expired id matches");
        assertEquals(16, result.bytesFreed, "part bytes reclaimed");
        assertEquals(0, manager.uploads.size(), "no uploads left");
    }

    private static void testFreshUploadSurvivesSweep() {
        reset();
        FakeClock clock = new FakeClock(1_000_000L);
        MultipartUploadManager manager = new MultipartUploadManager(service, 60_000L, clock::get);
        service.createBucket("fresh-bucket");
        String uploadId = manager.initiateMultipartUpload("fresh-bucket", "big.bin");
        String etag = manager.uploadPart(uploadId, 1, "0123456789ABCDEF".getBytes(StandardCharsets.UTF_8));
        clock.advance(30_000L);
        SweepResult result = manager.sweepExpiredUploads();
        assertEquals(0, result.expiredUploadIds.size(), "nothing expired");
        assertTrue(manager.uploads.containsKey(uploadId), "fresh upload kept");
        String composite = manager.completeMultipartUpload(uploadId, List.of(new CompletedPart(1, etag)));
        assertTrue(composite.endsWith("-1"), "still completes");
    }

    private static void testNoTtlMeansNoExpiry() {
        reset();
        FakeClock clock = new FakeClock(1_000_000L);
        MultipartUploadManager manager = new MultipartUploadManager(service, null, clock::get);
        service.createBucket("no-ttl-bucket");
        String uploadId = manager.initiateMultipartUpload("no-ttl-bucket", "big.bin");
        manager.uploadPart(uploadId, 1, new byte[]{1, 2, 3, 4});
        clock.advance(10_000_000L);
        SweepResult result = manager.sweepExpiredUploads();
        assertEquals(0, result.expiredUploadIds.size(), "no expiry without ttl");
        assertTrue(manager.uploads.containsKey(uploadId), "upload kept");
    }

    private static void testCompletedUploadIsNotSwept() {
        reset();
        FakeClock clock = new FakeClock(1_000_000L);
        MultipartUploadManager manager = new MultipartUploadManager(service, 60_000L, clock::get);
        service.createBucket("done-bucket");
        String uploadId = manager.initiateMultipartUpload("done-bucket", "big.bin");
        String etag = manager.uploadPart(uploadId, 1, "0123456789ABCDEF".getBytes(StandardCharsets.UTF_8));
        manager.completeMultipartUpload(uploadId, List.of(new CompletedPart(1, etag)));
        clock.advance(3_600_000L);
        SweepResult result = manager.sweepExpiredUploads();
        assertEquals(0, result.expiredUploadIds.size(), "completed upload not swept");
        assertArrayEquals("0123456789ABCDEF".getBytes(StandardCharsets.UTF_8),
            service.getObject("done-bucket", "big.bin", null), "completed object readable");
    }

    // --- assertion helpers (mirror v1 main-style test) ---

    private interface ThrowingRunnable {
        void run();
    }

    private static void expectThrows(ThrowingRunnable r, String message) {
        expectThrows(IllegalArgumentException.class, r, message);
    }

    private static void expectThrows(Class<? extends RuntimeException> type, ThrowingRunnable r, String message) {
        try {
            r.run();
        } catch (RuntimeException e) {
            if (type.isInstance(e)) {
                return;
            }
            throw new AssertionError(message + " - wrong exception type: " + e.getClass().getSimpleName());
        }
        throw new AssertionError(message + " - expected " + type.getSimpleName() + " but nothing was thrown");
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
        if (!condition) {
            throw new AssertionError(message);
        }
    }
}
