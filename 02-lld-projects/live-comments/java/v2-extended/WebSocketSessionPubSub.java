import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public class WebSocketSessionPubSub implements CommentFanoutService, LiveSessionRegistry {
    // streamId -> set of sessionIds
    private final Map<String, Set<String>> streamSubscriptions = new ConcurrentHashMap<>();
    private final Map<String, WebSocketConnection> activeConnections = new ConcurrentHashMap<>();

    public void addConnection(String sessionId, WebSocketConnection connection) {
        activeConnections.put(sessionId, connection);
    }

    @Override
    public void register(String streamId, String sessionId, String userId) {
        streamSubscriptions.computeIfAbsent(streamId, k -> ConcurrentHashMap.newKeySet()).add(sessionId);
    }

    @Override
    public void unregister(String streamId, String sessionId) {
        Set<String> sessions = streamSubscriptions.get(streamId);
        if (sessions != null) {
            sessions.remove(sessionId);
            if (sessions.isEmpty()) {
                streamSubscriptions.remove(streamId);
            }
        }
        activeConnections.remove(sessionId);
    }

    @Override
    public void fanout(String streamId, String commentPayload, long eventTimeMs) {
        Set<String> sessions = streamSubscriptions.get(streamId);
        if (sessions != null) {
            for (String sessionId : sessions) {
                WebSocketConnection conn = activeConnections.get(sessionId);
                if (conn != null) {
                    try {
                        conn.send(commentPayload);
                    } catch (Exception e) {
                        // ensure subscriber disconnect cannot block unrelated subscribers indefinitely
                        continue;
                    }
                }
            }
        }
    }
}
