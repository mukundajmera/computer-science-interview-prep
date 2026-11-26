package v1_basic;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;

public class LiveStreamPipelineTest {

    @Test
    public void testIngestServerStartEndSession() {
        LiveStreamIngestServer server = new LiveStreamIngestServer();
        assertTrue(server.startSession("stream_1"));
        assertTrue(server.isActive("stream_1"));
        assertFalse(server.startSession("stream_1"));
        
        assertTrue(server.endSession("stream_1"));
        assertFalse(server.isActive("stream_1"));
        assertFalse(server.endSession("stream_1"));
    }

    @Test
    public void testAbrTranscoderLadder() {
        AbrTranscoderLadder ladder = new AbrTranscoderLadder();
        Map<String, String> renditions = ladder.transcodeSegment("stream_1", 42);
        
        assertEquals(4, renditions.size());
        assertTrue(renditions.containsKey("1080p"));
        assertEquals("stream_1_720p_seg_42.ts", renditions.get("720p"));
    }

    @Test
    public void testLiveManifestManagerWindow() {
        LiveManifestManager manager = new LiveManifestManager(3);
        manager.appendSegment("stream_1", "1080p", "url_1");
        manager.appendSegment("stream_1", "1080p", "url_2");
        manager.appendSegment("stream_1", "1080p", "url_3");
        manager.appendSegment("stream_1", "1080p", "url_4");
        
        List<LiveManifestManager.Segment> manifest = manager.getManifest("stream_1");
        assertEquals(3, manifest.size());
        assertEquals("url_2", manifest.get(0).url);
        assertEquals("url_4", manifest.get(2).url);
    }

    @Test
    public void testOriginShieldTreeCaching() {
        OriginShieldTree shield = new OriginShieldTree();
        shield.writeToOrigin("seg_1", "video_data_1");
        
        // Fetch from origin, promotes to L1 and L2
        assertEquals("video_data_1", shield.fetch("seg_1"));
        assertEquals("video_data_1", shield.fetch("seg_1")); // from l1
        
        // Fetch missing
        assertNull(shield.fetch("seg_2"));
    }

    @Test
    public void testPipelineIntegration() {
        LiveStreamIngestServer ingest = new LiveStreamIngestServer();
        AbrTranscoderLadder transcoder = new AbrTranscoderLadder();
        LiveManifestManager manifestManager = new LiveManifestManager();
        OriginShieldTree shield = new OriginShieldTree();
        
        String streamId = "live_1";
        assertTrue(ingest.startSession(streamId));
        
        int segmentId = 1;
        Map<String, String> renditions = transcoder.transcodeSegment(streamId, segmentId);
        
        for (Map.Entry<String, String> entry : renditions.entrySet()) {
            String rendition = entry.getKey();
            String url = entry.getValue();
            shield.writeToOrigin(url, "data_for_" + url);
            manifestManager.appendSegment(streamId, rendition, url);
        }
        
        List<LiveManifestManager.Segment> manifest = manifestManager.getManifest(streamId);
        assertEquals(4, manifest.size());
        
        String urlToFetch = manifest.get(0).url;
        String data = shield.fetch(urlToFetch);
        assertEquals("data_for_" + urlToFetch, data);
    }
}
