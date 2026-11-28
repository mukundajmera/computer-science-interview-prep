import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class ObjectStorageServiceV2Test {

    private ObjectStorageServiceV2 service;
    private File tempDir;
    private final String bucket = "test-bucket";

    @BeforeEach
    public void setup() throws IOException {
        tempDir = Files.createTempDirectory("oss-v2-test").toFile();
        service = new ObjectStorageServiceV2(tempDir.getAbsolutePath());
        service.createBucket(bucket);
    }

    @AfterEach
    public void teardown() {
        for (File file : tempDir.listFiles()) {
            file.delete();
        }
        tempDir.delete();
    }

    private String onlyChunkId(String objKey) {
        return service.getMetadataStore().getObjectMetadata(bucket, objKey, null).chunks.get(0);
    }

    private long totalContainerBytes() {
        long total = 0;
        for (ChunkServerV2 server : service.getChunkServers()) {
            total += server.getContainerFile().length();
        }
        return total;
    }

    // --- Parity with the v1 test scenarios ---

    @Test
    public void testBucketAndObjectCrud() throws IOException {
        byte[] data = "Hello, Distributed World!".getBytes(StandardCharsets.UTF_8);
        service.putObject(bucket, "test_file.txt", data);
        assertArrayEquals(data, service.getObject(bucket, "test_file.txt"));

        service.putObject(bucket, "test_file2.txt", "Another file".getBytes(StandardCharsets.UTF_8));
        service.putObject(bucket, "other_file.txt", "Different prefix".getBytes(StandardCharsets.UTF_8));
        List<String> files = service.listObjects(bucket, "test_");
        assertEquals(2, files.size());
        assertTrue(files.contains("test_file.txt"));
        assertTrue(files.contains("test_file2.txt"));
    }

    @Test
    public void testObjectVersioningAndRollback() throws IOException {
        String v1Id = service.putObject(bucket, "versioned.txt", "Version 1".getBytes(StandardCharsets.UTF_8));
        String v2Id = service.putObject(bucket, "versioned.txt", "Version 2".getBytes(StandardCharsets.UTF_8));

        assertArrayEquals("Version 2".getBytes(StandardCharsets.UTF_8), service.getObject(bucket, "versioned.txt"));
        assertArrayEquals("Version 1".getBytes(StandardCharsets.UTF_8),
                service.getObject(bucket, "versioned.txt", v1Id));

        service.deleteObject(bucket, "versioned.txt");
        assertNull(service.getObject(bucket, "versioned.txt"));
        assertArrayEquals("Version 2".getBytes(StandardCharsets.UTF_8),
                service.getObject(bucket, "versioned.txt", v2Id));
    }

    @Test
    public void testMultipartUploadWorkflow() throws IOException {
        String uploadId = service.initiateMultipartUpload(bucket, "large_file.txt");
        service.uploadPart(uploadId, 1, "Part 1 ".getBytes(StandardCharsets.UTF_8));
        service.uploadPart(uploadId, 2, "Part 2 ".getBytes(StandardCharsets.UTF_8));
        service.uploadPart(uploadId, 3, "Part 3".getBytes(StandardCharsets.UTF_8));
        service.completeMultipartUpload(uploadId);
        assertArrayEquals("Part 1 Part 2 Part 3".getBytes(StandardCharsets.UTF_8),
                service.getObject(bucket, "large_file.txt"));
    }

    @Test
    public void testChecksumValidationAndTamperDetection() throws IOException {
        byte[] data = "Important Data".getBytes(StandardCharsets.UTF_8);
        service.putObject(bucket, "secure.txt", data);

        String chunkId = onlyChunkId("secure.txt");
        int hashVal = Math.abs(chunkId.hashCode());
        ChunkServerV2 target = service.getChunkServers().get(hashVal % service.getChunkServers().size());

        ChunkServerV2.ChunkInfo info = target.getChunkInfo(chunkId);
        try (RandomAccessFile raf = new RandomAccessFile(target.getContainerFile(), "rw")) {
            raf.seek(info.offset);
            raf.write("Corrupted Data".getBytes(StandardCharsets.UTF_8)); // same length, corrupt payload
        }

        assertArrayEquals(data, service.getObject(bucket, "secure.txt"));
        // Read repair rewrote the corrupted replica.
        assertArrayEquals(data, target.readChunk(chunkId));
    }

    @Test
    public void testBlockCompactionAndTombstoneClean() throws IOException {
        service.putObject(bucket, "file1.txt", "File 1".getBytes(StandardCharsets.UTF_8));
        service.putObject(bucket, "file2.txt", "File 2 V1".getBytes(StandardCharsets.UTF_8));
        service.putObject(bucket, "file2.txt", "File 2 V2".getBytes(StandardCharsets.UTF_8));
        service.deleteObject(bucket, "file1.txt");

        long before = totalContainerBytes();
        java.util.Set<String> active = new java.util.HashSet<>(
                service.getMetadataStore().getObjectMetadata(bucket, "file2.txt", null).chunks);
        for (ChunkServerV2 server : service.getChunkServers()) {
            server.compact(active);
        }
        assertTrue(totalContainerBytes() < before);
    }

    // --- Improvement #2: self-describing frames + index rebuild ---

    @Test
    public void testIndexRebuildRestoresReads() throws IOException {
        service.putObject(bucket, "a.txt", "data a".getBytes(StandardCharsets.UTF_8));
        service.putObject(bucket, "b.txt", "data b".getBytes(StandardCharsets.UTF_8));
        ChunkServerV2 server = service.getChunkServers().get(0);
        // Every chunk lands on every server with replication factor 3.
        int indexedBefore = 2;

        // Wipe the in-memory index entirely, then rebuild from the container.
        for (String key : new String[]{"a.txt", "b.txt"}) {
            server.simulateChunkLoss(onlyChunkId(key));
        }
        int recovered = server.rebuildIndexFromContainer();

        assertEquals(indexedBefore, recovered);
        assertArrayEquals("data a".getBytes(StandardCharsets.UTF_8), service.getObject(bucket, "a.txt"));
    }

    @Test
    public void testRebuildToleratesTruncatedTail() throws IOException {
        service.putObject(bucket, "a.txt", "data a".getBytes(StandardCharsets.UTF_8));
        ChunkServerV2 server = service.getChunkServers().get(0);
        String chunkId = onlyChunkId("a.txt");
        // A torn write leaves trailing garbage after the last full frame.
        try (RandomAccessFile raf = new RandomAccessFile(server.getContainerFile(), "rw")) {
            raf.seek(raf.length());
            raf.write(new byte[]{0x43, 0x48, 0x4B, 0x31, 0x00, 0x00});
        }

        int recovered = server.rebuildIndexFromContainer();
        assertTrue(recovered >= 1);
        assertArrayEquals("data a".getBytes(StandardCharsets.UTF_8), server.readChunk(chunkId));
    }

    // --- Improvement #1: throttled repair + failure injection ---

    @Test
    public void testRepairPassRestoresReplicasAfterChunkLoss() throws IOException {
        byte[] data = "replicate me".getBytes(StandardCharsets.UTF_8);
        service.putObject(bucket, "a.txt", data);
        String chunkId = onlyChunkId("a.txt");
        int hashVal = Math.abs(chunkId.hashCode());
        ChunkServerV2 victim = service.getChunkServers().get(hashVal % service.getChunkServers().size());
        victim.simulateChunkLoss(chunkId);
        assertFalse(victim.hasChunk(chunkId));

        List<String> repaired = service.repairPass();

        assertEquals(1, repaired.size());
        assertEquals(chunkId, repaired.get(0));
        assertTrue(victim.hasChunk(chunkId));
        assertArrayEquals(data, victim.readChunk(chunkId));
    }

    @Test
    public void testRepairPassRespectsByteBudget() throws IOException {
        service.putObject(bucket, "a.txt", new byte[30]);
        String chunkId = onlyChunkId("a.txt");
        int hashVal = Math.abs(chunkId.hashCode());
        ChunkServerV2 victim = service.getChunkServers().get(hashVal % service.getChunkServers().size());
        victim.simulateChunkLoss(chunkId);

        assertTrue(service.repairPass(29).isEmpty());
        assertFalse(victim.hasChunk(chunkId));

        List<String> repaired = service.repairPass(30);
        assertEquals(1, repaired.size());
        assertTrue(victim.hasChunk(chunkId));
    }

    @Test
    public void testReadsSkipDownServer() throws IOException {
        byte[] data = "still readable".getBytes(StandardCharsets.UTF_8);
        service.putObject(bucket, "a.txt", data);
        String chunkId = onlyChunkId("a.txt");
        int hashVal = Math.abs(chunkId.hashCode());
        ChunkServerV2 downServer = service.getChunkServers().get(hashVal % service.getChunkServers().size());
        downServer.setDown(true);

        assertArrayEquals(data, service.getObject(bucket, "a.txt"));
        assertThrows(IllegalStateException.class, () -> downServer.readChunk(chunkId));

        downServer.setDown(false);
        assertArrayEquals(data, service.getObject(bucket, "a.txt"));
    }

    @Test
    public void testWritesSucceedWithOneReplicaDown() throws IOException {
        service.getChunkServers().get(0).setDown(true);
        service.putObject(bucket, "a.txt", "written during outage".getBytes(StandardCharsets.UTF_8));
        service.getChunkServers().get(0).setDown(false);

        assertArrayEquals("written during outage".getBytes(StandardCharsets.UTF_8),
                service.getObject(bucket, "a.txt"));
        // The read repaired the replica that missed the write.
        assertTrue(service.getChunkServers().get(0).hasChunk(onlyChunkId("a.txt")));
    }

    // --- Improvement #3: version retention + garbage collection ---

    @Test
    public void testVersionRetentionGcDropsOldVersions() throws IOException {
        String v1Id = service.putObject(bucket, "doc.txt", "draft 1".getBytes(StandardCharsets.UTF_8));
        String v2Id = service.putObject(bucket, "doc.txt", "draft 2".getBytes(StandardCharsets.UTF_8));
        service.putObject(bucket, "doc.txt", "final".getBytes(StandardCharsets.UTF_8));

        long before = totalContainerBytes();
        List<String> pruned = service.collectGarbage(1);
        long after = totalContainerBytes();

        assertEquals(2, pruned.size()); // one chunk per pruned version
        assertArrayEquals("final".getBytes(StandardCharsets.UTF_8), service.getObject(bucket, "doc.txt"));
        assertNull(service.getObject(bucket, "doc.txt", v1Id));
        assertNull(service.getObject(bucket, "doc.txt", v2Id));
        assertTrue(after < before);
    }

    @Test
    public void testRetentionPreservesLatestDeleteMarker() throws IOException {
        service.putObject(bucket, "doc.txt", "gone soon".getBytes(StandardCharsets.UTF_8));
        service.deleteObject(bucket, "doc.txt");

        service.collectGarbage(1);

        assertNull(service.getObject(bucket, "doc.txt"));
        assertTrue(service.listObjects(bucket, "").isEmpty());
    }

    @Test
    public void testVersionsKeptWithoutPolicy() throws IOException {
        String v1Id = service.putObject(bucket, "doc.txt", "one".getBytes(StandardCharsets.UTF_8));
        service.putObject(bucket, "doc.txt", "two".getBytes(StandardCharsets.UTF_8));

        assertThrows(IllegalStateException.class, () -> service.collectGarbage(null));
        assertArrayEquals("one".getBytes(StandardCharsets.UTF_8),
                service.getObject(bucket, "doc.txt", v1Id));
        assertArrayEquals("two".getBytes(StandardCharsets.UTF_8), service.getObject(bucket, "doc.txt"));
    }

    @Test
    public void testConfiguredRetentionPolicyAppliesByDefault() throws IOException {
        ObjectStorageServiceV2 configured = new ObjectStorageServiceV2(
                Files.createTempDirectory("oss-v2-retention").toFile().getAbsolutePath(), 2);
        configured.createBucket("b2");
        String first = configured.putObject("b2", "k", "v1".getBytes(StandardCharsets.UTF_8));
        String second = configured.putObject("b2", "k", "v2".getBytes(StandardCharsets.UTF_8));
        configured.putObject("b2", "k", "v3".getBytes(StandardCharsets.UTF_8));

        configured.collectGarbage(null);

        assertNull(configured.getObject("b2", "k", first));
        assertArrayEquals("v2".getBytes(StandardCharsets.UTF_8), configured.getObject("b2", "k", second));
        assertArrayEquals("v3".getBytes(StandardCharsets.UTF_8), configured.getObject("b2", "k"));
    }
}
