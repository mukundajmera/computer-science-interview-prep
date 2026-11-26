import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.List;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

public class ObjectStorageServiceTest {

    private ObjectStorageService service;
    private File tempDir;
    private final String bucket = "test-bucket";

    @BeforeEach
    public void setup() throws IOException {
        tempDir = Files.createTempDirectory("oss-test").toFile();
        service = new ObjectStorageService(tempDir.getAbsolutePath());
        service.createBucket(bucket);
    }

    @AfterEach
    public void teardown() {
        deleteDir(tempDir);
    }

    private void deleteDir(File file) {
        File[] contents = file.listFiles();
        if (contents != null) {
            for (File f : contents) {
                deleteDir(f);
            }
        }
        file.delete();
    }

    @Test
    public void testPutAndGetObjectWithIntegrityCheck() throws IOException {
        byte[] data = "Hello, Distributed World!".getBytes(StandardCharsets.UTF_8);
        service.putObject(bucket, "test_file.txt", data);
        
        byte[] retrieved = service.getObject(bucket, "test_file.txt");
        assertNotNull(retrieved);
        assertArrayEquals(data, retrieved);
        
        service.putObject(bucket, "test_file2.txt", "Another file".getBytes(StandardCharsets.UTF_8));
        service.putObject(bucket, "other_file.txt", "Different prefix".getBytes(StandardCharsets.UTF_8));
        
        List<String> files = service.listObjects(bucket, "test_");
        assertEquals(2, files.size());
        assertTrue(files.contains("test_file.txt"));
        assertTrue(files.contains("test_file2.txt"));
    }

    @Test
    public void testObjectVersioningAndTombstoneDelete() throws IOException {
        // Version 1
        byte[] v1Data = "Version 1".getBytes(StandardCharsets.UTF_8);
        String v1Id = service.putObject(bucket, "versioned.txt", v1Data);
        
        // Version 2
        byte[] v2Data = "Version 2".getBytes(StandardCharsets.UTF_8);
        String v2Id = service.putObject(bucket, "versioned.txt", v2Data);
        
        // Default get should return v2
        assertArrayEquals(v2Data, service.getObject(bucket, "versioned.txt"));
        
        // Get specific version
        assertArrayEquals(v1Data, service.getObject(bucket, "versioned.txt", v1Id));
        
        // Delete object creates a tombstone
        service.deleteObject(bucket, "versioned.txt");
        assertNull(service.getObject(bucket, "versioned.txt"));
        
        // Previous versions still accessible
        assertArrayEquals(v2Data, service.getObject(bucket, "versioned.txt", v2Id));
    }

    @Test
    public void testMultipartUploadFlowAndReassembly() throws IOException {
        String uploadId = service.initiateMultipartUpload(bucket, "large_file.txt");
        
        byte[] part1 = "Part 1 ".getBytes(StandardCharsets.UTF_8);
        byte[] part2 = "Part 2 ".getBytes(StandardCharsets.UTF_8);
        byte[] part3 = "Part 3".getBytes(StandardCharsets.UTF_8);
        
        service.uploadPart(uploadId, 1, part1);
        service.uploadPart(uploadId, 2, part2);
        service.uploadPart(uploadId, 3, part3);
        
        service.completeMultipartUpload(uploadId);
        
        byte[] retrieved = service.getObject(bucket, "large_file.txt");
        assertNotNull(retrieved);
        
        String expectedStr = "Part 1 Part 2 Part 3";
        assertArrayEquals(expectedStr.getBytes(StandardCharsets.UTF_8), retrieved);
    }

    @Test
    public void testChunkCorruptionDetectionViaChecksum() throws IOException {
        byte[] data = "Important Data".getBytes(StandardCharsets.UTF_8);
        service.putObject(bucket, "secure.txt", data);
        
        MetadataStore.ObjectMetadata metadata = service.getMetadataStore().getObjectMetadata(bucket, "secure.txt", null);
        String chunkId = metadata.chunks.get(0);
        
        // Corrupt data on the first replica
        int hashVal = Math.abs(chunkId.hashCode());
        ChunkServer targetReplica = service.getChunkServers().get(hashVal % service.getChunkServers().size());
        
        ChunkServer.ChunkInfo info = targetReplica.getChunkInfo(chunkId);
        try (RandomAccessFile raf = new RandomAccessFile(targetReplica.getContainerFile(), "rw")) {
            raf.seek(info.offset);
            raf.write("Corrupted Data".getBytes(StandardCharsets.UTF_8));
        }
        
        // Get should succeed via other replicas and trigger read-repair
        byte[] retrieved = service.getObject(bucket, "secure.txt");
        assertNotNull(retrieved);
        assertArrayEquals(data, retrieved);
        
        // Verify repair happened
        byte[] repairedData = targetReplica.readChunk(chunkId);
        assertArrayEquals(data, repairedData);
    }

    @Test
    public void testPrefixListingFilter() throws IOException {
        service.putObject(bucket, "file1.txt", "File 1".getBytes(StandardCharsets.UTF_8));
        service.putObject(bucket, "file2.txt", "File 2 V1".getBytes(StandardCharsets.UTF_8));
        service.putObject(bucket, "file2.txt", "File 2 V2".getBytes(StandardCharsets.UTF_8));
        service.deleteObject(bucket, "file1.txt");
        
        long sizesBefore = 0;
        for (ChunkServer server : service.getChunkServers()) {
            sizesBefore += server.getContainerFile().length();
        }
        
        // Simulate GC by finding active chunks of the latest object only
        Set<String> activeChunks = new java.util.HashSet<>();
        MetadataStore.ObjectMetadata metadata = service.getMetadataStore().getObjectMetadata(bucket, "file2.txt", null);
        activeChunks.addAll(metadata.chunks);
        
        // Compact manually with active chunks
        for (ChunkServer server : service.getChunkServers()) {
            server.compact(activeChunks);
        }
        
        long sizesAfter = 0;
        for (ChunkServer server : service.getChunkServers()) {
            sizesAfter += server.getContainerFile().length();
        }
        
        assertTrue(sizesAfter < sizesBefore);
    }
}