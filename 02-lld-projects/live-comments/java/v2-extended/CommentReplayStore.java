import java.util.List;

public interface CommentReplayStore {
    List<String> replay(String streamId, String cursor, int limit);
}
