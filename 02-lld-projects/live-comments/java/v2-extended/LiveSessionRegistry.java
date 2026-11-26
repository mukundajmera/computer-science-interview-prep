public interface LiveSessionRegistry {
    void register(String streamId, String sessionId, String userId);
    void unregister(String streamId, String sessionId);
}
