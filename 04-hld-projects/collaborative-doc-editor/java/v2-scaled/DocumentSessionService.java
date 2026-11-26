package collab.v2;

import java.util.List;

public interface DocumentSessionService {
    SessionToken joinSession(String documentId, String userId, long lastSeenOperationId);
    void publishCursor(String documentId, String userId, int position);
    void leaveSession(String documentId, String userId);
}

interface OperationLogStore {
    void append(OperationEvent event);
    List<OperationEvent> replay(String documentId, long afterOperationId, int limit);
}

final class SessionToken {
    public final String documentId;
    public final String userId;
    public final long streamOffset;

    SessionToken(String documentId, String userId, long streamOffset) {
        this.documentId = documentId;
        this.userId = userId;
        this.streamOffset = streamOffset;
    }
}

final class OperationEvent {
    public final long operationId;
    public final String documentId;
    public final String payload;

    OperationEvent(long operationId, String documentId, String payload) {
        this.operationId = operationId;
        this.documentId = documentId;
        this.payload = payload;
    }
}
