import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class ChunkedBlobUploaderTest {

    private ChunkedBlobUploader uploader;

    @BeforeEach
    void setUp() {
        uploader = new ChunkedBlobUploader();
    }

    @Test
    void testSuccessfulUploadAndRetrieval() {
        byte[] chunk1 = "Hello, ".getBytes();
        byte[] chunk2 = "World!".getBytes();
        byte[] fullData = "Hello, World!".getBytes();
        String expectedSha256 = ChunkedBlobUploader.computeSha256(fullData);

        String sessionId = uploader.initiateSession("blob-1", 2, fullData.length, expectedSha256);
        assertNotNull(sessionId);

        uploader.uploadChunk(sessionId, 0, chunk1);
        List<Integer> missingChunks = uploader.getMissingChunks(sessionId);
        assertEquals(1, missingChunks.size());
        assertTrue(missingChunks.contains(1));

        uploader.uploadChunk(sessionId, 1, chunk2);
        assertTrue(uploader.getMissingChunks(sessionId).isEmpty());

        assertTrue(uploader.completeSession(sessionId));

        byte[] retrieved = uploader.getBlob("blob-1");
        assertNotNull(retrieved);
        assertArrayEquals(fullData, retrieved);
    }

    @Test
    void testUploadWithInvalidSession() {
        assertThrows(IllegalArgumentException.class, () -> uploader.uploadChunk("invalid-session", 0, new byte[1]));
        assertThrows(IllegalArgumentException.class, () -> uploader.getMissingChunks("invalid-session"));
        assertThrows(IllegalArgumentException.class, () -> uploader.completeSession("invalid-session"));
    }

    @Test
    void testIncompleteSessionCompletion() {
        byte[] chunk1 = "Hello, ".getBytes();
        byte[] fullData = "Hello, World!".getBytes();
        String expectedSha256 = ChunkedBlobUploader.computeSha256(fullData);

        String sessionId = uploader.initiateSession("blob-2", 2, fullData.length, expectedSha256);

        uploader.uploadChunk(sessionId, 0, chunk1);

        assertFalse(uploader.completeSession(sessionId));
        assertNull(uploader.getBlob("blob-2"));
    }

    @Test
    void testChecksumMismatch() {
        byte[] chunk1 = "Hello, ".getBytes();
        byte[] chunk2 = "Wrong!".getBytes(); // Incorrect data
        byte[] fullData = "Hello, World!".getBytes();
        String expectedSha256 = ChunkedBlobUploader.computeSha256(fullData);

        String sessionId = uploader.initiateSession("blob-3", 2, fullData.length, expectedSha256);

        uploader.uploadChunk(sessionId, 0, chunk1);
        uploader.uploadChunk(sessionId, 1, chunk2);

        assertThrows(IllegalStateException.class, () -> uploader.completeSession(sessionId));
        assertNull(uploader.getBlob("blob-3"));
    }

    @Test
    void testInvalidChunkIndex() {
        byte[] fullData = "Test".getBytes();
        String expectedSha256 = ChunkedBlobUploader.computeSha256(fullData);
        String sessionId = uploader.initiateSession("blob-4", 1, fullData.length, expectedSha256);

        assertThrows(IllegalArgumentException.class, () -> uploader.uploadChunk(sessionId, -1, fullData));
        assertThrows(IllegalArgumentException.class, () -> uploader.uploadChunk(sessionId, 1, fullData)); // Only 1 chunk, max index is 0
    }
}
