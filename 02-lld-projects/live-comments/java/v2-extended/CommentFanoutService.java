public interface CommentFanoutService {
    void fanout(String streamId, String commentPayload, long eventTimeMs);
}
