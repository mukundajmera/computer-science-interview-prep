public interface WindowStateStore {
    void save(String windowKey, String statePayload);
    String load(String windowKey);
}
