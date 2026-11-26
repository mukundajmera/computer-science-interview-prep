package v1_basic;

import java.util.HashMap;
import java.util.Map;
import java.util.Arrays;
import java.util.List;

public class AbrTranscoderLadder {
    private final List<String> renditions = Arrays.asList("1080p", "720p", "480p", "360p");

    public Map<String, String> transcodeSegment(String streamId, int segmentId) {
        Map<String, String> transcoded = new HashMap<>();
        for (String rendition : renditions) {
            transcoded.put(rendition, streamId + "_" + rendition + "_seg_" + segmentId + ".ts");
        }
        return transcoded;
    }
}
