package v2_extended;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * v2 AbrTranscoderLadder: v1 parity plus improvement #2, transcoder node
 * failure recovery with time-aligned keyframes (FOLLOW-UPS.md #1,
 * PITFALLS.md #4). See OriginShieldTree for the full v2 list.
 */
public class AbrTranscoderLadder {

    public static class RenditionOutput {
        public final String url;
        public final String node;
        public final double keyframeTs;

        public RenditionOutput(String url, String node, double keyframeTs) {
            this.url = url;
            this.node = node;
            this.keyframeTs = keyframeTs;
        }
    }

    private final List<String> renditions = Arrays.asList("1080p", "720p", "480p", "360p");
    private final List<String> nodes;
    private final Set<String> deadNodes = new HashSet<>();

    public AbrTranscoderLadder(List<String> nodes) {
        this.nodes = new ArrayList<>(nodes);
    }

    public AbrTranscoderLadder() {
        this(Arrays.asList("gpu-1"));
    }

    /** Failure injection: mark a transcode node dead. */
    public synchronized void failNode(String nodeId) {
        deadNodes.add(nodeId);
    }

    public synchronized void reviveNode(String nodeId) {
        deadNodes.remove(nodeId);
    }

    /** v1-compatible signature and output: rendition -> segment URL. */
    public Map<String, String> transcodeSegment(String streamId, int segmentId) {
        Map<String, String> transcoded = new HashMap<>();
        for (String rendition : renditions) {
            transcoded.put(rendition, streamId + "_" + rendition + "_seg_" + segmentId + ".ts");
        }
        return transcoded;
    }

    /**
     * Transcode on live nodes with failover and aligned keyframes.
     *
     * Each rendition runs on a live node; dead nodes are skipped so one
     * dead GPU node never drops the stream (FOLLOW-UPS.md #1). Every
     * rendition carries the same keyframe timestamp, aligned down to the
     * keyframe interval, so ABR switches are seamless (PITFALLS.md #4).
     */
    public Map<String, RenditionOutput> transcodeSegmentResilient(
            String streamId, int segmentId, double keyframeIntervalSeconds) {
        List<String> liveNodes = new ArrayList<>();
        synchronized (this) {
            for (String node : nodes) {
                if (!deadNodes.contains(node)) {
                    liveNodes.add(node);
                }
            }
        }
        if (liveNodes.isEmpty()) {
            throw new IllegalStateException("NoLiveTranscodeNodes: all transcode nodes are down");
        }

        // Same aligned IDR boundary for every rendition of this segment.
        double segmentTime = segmentId * keyframeIntervalSeconds;
        double alignedKeyframe = Math.floor(segmentTime / keyframeIntervalSeconds) * keyframeIntervalSeconds;

        Map<String, RenditionOutput> output = new HashMap<>();
        for (int i = 0; i < renditions.size(); i++) {
            String rendition = renditions.get(i);
            String node = liveNodes.get(i % liveNodes.size());
            output.put(rendition, new RenditionOutput(
                    streamId + "_" + rendition + "_seg_" + segmentId + ".ts",
                    node,
                    alignedKeyframe));
        }
        return output;
    }

    public Map<String, RenditionOutput> transcodeSegmentResilient(String streamId, int segmentId) {
        return transcodeSegmentResilient(streamId, segmentId, 2.0);
    }
}
