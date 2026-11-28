package v2_extended;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class LiveStreamPipelineV2Test {

    // ------------------------------------------------------------------
    // v1 parity tests: same scenarios as tests/v1_basic, run against v2.
    // ------------------------------------------------------------------

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
            String url = entry.getValue();
            shield.writeToOrigin(url, "data_for_" + url);
            manifestManager.appendSegment(streamId, entry.getKey(), url);
        }

        List<LiveManifestManager.Segment> manifest = manifestManager.getManifest(streamId);
        assertEquals(4, manifest.size());

        String urlToFetch = manifest.get(0).url;
        String data = shield.fetch(urlToFetch);
        assertEquals("data_for_" + urlToFetch, data);
    }

    // ------------------------------------------------------------------
    // v2-only tests: one or more per improvement.
    // ------------------------------------------------------------------

    // Improvement #1: singleflight, LRU bounds, origin metrics
    // (FOLLOW-UPS.md #2, PITFALLS.md #2).

    @Test
    public void testSingleflightCollapsesConcurrentMisses() throws InterruptedException {
        AtomicInteger loadCalls = new AtomicInteger(0);
        OriginShieldTree shield = new OriginShieldTree(-1, key -> {
            loadCalls.incrementAndGet();
            try {
                Thread.sleep(200); // slow origin: exposes uncollapsed duplicate loads
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return "data_" + key;
        });

        int viewers = 8;
        CountDownLatch start = new CountDownLatch(1);
        CountDownLatch done = new CountDownLatch(viewers);
        List<String> results = new ArrayList<>();
        for (int i = 0; i < viewers; i++) {
            new Thread(() -> {
                try {
                    start.await();
                    synchronized (results) {
                        results.add(shield.fetch("seg_hot"));
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    done.countDown();
                }
            }).start();
        }
        start.countDown();
        assertTrue(done.await(5, TimeUnit.SECONDS));

        assertEquals(viewers, results.size());
        for (String r : results) {
            assertEquals("data_seg_hot", r);
        }
        assertEquals(1, loadCalls.get(), "8 concurrent viewers must cause exactly one origin load");
        assertEquals(1, shield.getOriginReads());
    }

    @Test
    public void testLruEvictionBoundsTiers() {
        OriginShieldTree shield = new OriginShieldTree(2);
        for (int i = 0; i < 3; i++) {
            shield.writeToOrigin("seg_" + i, "data_" + i);
            shield.fetch("seg_" + i);
        }

        // L1 holds only the 2 most recently used segments.
        assertEquals(2, shield.l1Size());
        assertFalse(shield.l1Contains("seg_0"));
        assertTrue(shield.l1Contains("seg_1"));
        assertTrue(shield.l1Contains("seg_2"));
        // Evicted data is still served from the origin.
        assertEquals("data_0", shield.fetch("seg_0"));
    }

    @Test
    public void testOriginReadsMetricCountsOnlyTierMisses() {
        OriginShieldTree shield = new OriginShieldTree();
        shield.writeToOrigin("a", "1");
        shield.writeToOrigin("b", "2");

        shield.fetch("a"); // origin read
        shield.fetch("a"); // L1 hit
        shield.fetch("b"); // origin read
        shield.fetch("b"); // L1 hit

        assertEquals(2, shield.getOriginReads());
    }

    // Improvement #2: node failover and aligned keyframes
    // (FOLLOW-UPS.md #1, PITFALLS.md #4).

    @Test
    public void testTranscoderFailoverSkipsDeadNode() {
        AbrTranscoderLadder ladder = new AbrTranscoderLadder(Arrays.asList("gpu-1", "gpu-2"));
        ladder.failNode("gpu-1");

        Map<String, AbrTranscoderLadder.RenditionOutput> out = ladder.transcodeSegmentResilient("s1", 7);
        Set<String> usedNodes = new HashSet<>();
        for (AbrTranscoderLadder.RenditionOutput entry : out.values()) {
            usedNodes.add(entry.node);
        }
        assertEquals(Set.of("gpu-2"), usedNodes, "all renditions must move to the live node");
        assertEquals(4, out.size());
    }

    @Test
    public void testTranscoderAllNodesDeadRaises() {
        AbrTranscoderLadder ladder = new AbrTranscoderLadder(Arrays.asList("gpu-1", "gpu-2"));
        ladder.failNode("gpu-1");
        ladder.failNode("gpu-2");

        assertThrows(IllegalStateException.class, () -> ladder.transcodeSegmentResilient("s1", 7));
    }

    @Test
    public void testKeyframesAlignedAcrossRenditions() {
        AbrTranscoderLadder ladder = new AbrTranscoderLadder(Arrays.asList("gpu-1", "gpu-2"));
        Map<String, AbrTranscoderLadder.RenditionOutput> out =
                ladder.transcodeSegmentResilient("s1", 5, 2.0);

        Set<Double> keyframes = new HashSet<>();
        for (AbrTranscoderLadder.RenditionOutput entry : out.values()) {
            keyframes.add(entry.keyframeTs);
        }
        assertEquals(1, keyframes.size(), "every rendition of a segment shares one IDR boundary");
        // segmentTime = 5 * 2.0 = 10.0, aligned down to the 2s interval = 10.0
        assertEquals(10.0, keyframes.iterator().next(), 0.0001);
    }

    // Improvement #3: live-to-VOD archival (FOLLOW-UPS.md #4).

    @Test
    public void testArchiveVodKeepsFullHistoryBeyondWindow() {
        LiveManifestManager manager = new LiveManifestManager(3);
        for (int i = 0; i < 6; i++) {
            manager.appendSegment("s1", "1080p", "url_" + i);
        }

        List<LiveManifestManager.Segment> live = manager.getManifest("s1");
        assertEquals(3, live.size(), "live window still slides");
        assertEquals("url_3", live.get(0).url);

        List<LiveManifestManager.Segment> vod = manager.archiveVod("s1");
        assertEquals(6, vod.size(), "VOD asset keeps every segment");
        for (int i = 0; i < 6; i++) {
            assertEquals("url_" + i, vod.get(i).url);
        }
    }

    @Test
    public void testArchiveVodIdempotentAndUnknownStream() {
        LiveManifestManager manager = new LiveManifestManager();
        manager.appendSegment("s1", "720p", "url_0");

        List<LiveManifestManager.Segment> first = manager.archiveVod("s1");
        List<LiveManifestManager.Segment> second = manager.archiveVod("s1");
        assertEquals(first.size(), second.size());
        assertEquals(first.get(0).url, second.get(0).url);
        assertTrue(manager.archiveVod("never_streamed").isEmpty());
    }
}
