package video.v1;

import org.junit.jupiter.api.Test;
import java.util.Optional;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

class VideoServiceTest {

    static class InMemoryVideoService implements VideoService {
        private final Map<String, UploadSession> sessions = new HashMap<>();
        private final Map<String, Video> videos = new HashMap<>();
        private final Map<String, Manifest> manifests = new HashMap<>();

        @Override
        public UploadSession initUpload(InitUploadCommand command) {
            String sessionId = UUID.randomUUID().toString();
            String videoId = UUID.randomUUID().toString();
            UploadSession session = new UploadSession(sessionId, videoId, UploadStatus.INITIATED, command.expectedParts, 0);
            sessions.put(sessionId, session);
            videos.put(videoId, new Video(videoId, command.ownerId, UploadStatus.INITIATED));
            return session;
        }

        @Override
        public UploadSession uploadPart(String sessionId, int partNumber, String etag) {
            UploadSession session = sessions.get(sessionId);
            if (session == null) {
                throw new IllegalArgumentException("Session not found");
            }
            
            UploadSession updated = new UploadSession(sessionId, session.videoId, 
                UploadStatus.PARTIAL, session.expectedParts, session.uploadedParts + 1);
            sessions.put(sessionId, updated);
            return updated;
        }

        @Override
        public Video completeUpload(String sessionId, String idempotencyKey) {
            UploadSession session = sessions.get(sessionId);
            if (session == null) {
                throw new IllegalArgumentException("Session not found");
            }
            
            Video video = videos.get(session.videoId);
            Video updatedVideo = new Video(video.videoId, video.ownerId, UploadStatus.READY);
            videos.put(session.videoId, updatedVideo);
            
            manifests.put(session.videoId, new Manifest(session.videoId, "/path/to/" + session.videoId, "ready"));
            
            return updatedVideo;
        }

        @Override
        public Optional<Manifest> getManifest(String videoId) {
            return Optional.ofNullable(manifests.get(videoId));
        }
    }

    @Test
    void testInitUpload() {
        VideoService service = new InMemoryVideoService();
        InitUploadCommand cmd = new InitUploadCommand("user-1", "My Video", 10000L, 5);
        
        Object resultObj = service.initUpload(cmd);
        assertTrue(resultObj instanceof UploadSession);
        UploadSession session = (UploadSession) resultObj;
        
        assertEquals(UploadStatus.INITIATED, session.status);
        assertEquals(5, session.expectedParts);
        assertEquals(0, session.uploadedParts);
        assertNotNull(session.sessionId);
        assertNotNull(session.videoId);
    }

    @Test
    void testUploadPart() {
        VideoService service = new InMemoryVideoService();
        InitUploadCommand cmd = new InitUploadCommand("user-1", "My Video", 10000L, 5);
        UploadSession initialSession = service.initUpload(cmd);
        
        Object resultObj = service.uploadPart(initialSession.sessionId, 1, "etag-1");
        assertTrue(resultObj instanceof UploadSession);
        UploadSession session = (UploadSession) resultObj;
        
        assertEquals(UploadStatus.PARTIAL, session.status);
        assertEquals(1, session.uploadedParts);
        assertEquals(initialSession.sessionId, session.sessionId);
    }

    @Test
    void testCompleteUpload() {
        VideoService service = new InMemoryVideoService();
        InitUploadCommand cmd = new InitUploadCommand("user-1", "My Video", 10000L, 5);
        UploadSession initialSession = service.initUpload(cmd);
        service.uploadPart(initialSession.sessionId, 1, "etag-1");
        
        Object resultObj = service.completeUpload(initialSession.sessionId, "key-123");
        assertTrue(resultObj instanceof Video);
        Video video = (Video) resultObj;
        
        assertEquals(UploadStatus.READY, video.status);
        assertEquals(initialSession.videoId, video.videoId);
        assertEquals("user-1", video.ownerId);
        
        Optional<Manifest> manifestOpt = service.getManifest(video.videoId);
        assertTrue(manifestOpt.isPresent());
        assertEquals("ready", manifestOpt.get().state);
    }
}
