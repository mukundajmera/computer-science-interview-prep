
package metrics.v3;

import java.util.List;

public interface DistributedTopKService {
    void ingestView(String videoId, long timestampMs, String partitionKey);
    List<String> topK(String windowKey, int k, String region);
    void replayWindow(String windowKey, String replayToken);
}
