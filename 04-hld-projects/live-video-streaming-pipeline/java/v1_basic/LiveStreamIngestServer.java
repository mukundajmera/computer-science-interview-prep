package v1_basic;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class LiveStreamIngestServer {
    private final Map<String, Long> activeSessions = new ConcurrentHashMap<>();

    public boolean startSession(String streamId) {
        return activeSessions.putIfAbsent(streamId, System.currentTimeMillis()) == null;
    }

    public boolean endSession(String streamId) {
        return activeSessions.remove(streamId) != null;
    }

    public boolean isActive(String streamId) {
        return activeSessions.containsKey(streamId);
    }
}
