
package metrics.v2;

import java.util.List;

public interface WindowedTopKService {
    void ingestView(String videoId, long timestampMs);
    List<String> topK(String windowKey, int k);
}
