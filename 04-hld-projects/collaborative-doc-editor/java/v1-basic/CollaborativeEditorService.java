package collab.v1;

import java.util.Optional;

public interface CollaborativeEditorService {
    Document createDocument(String ownerId, String title);
    Optional<Document> getDocument(String documentId, String userId);
    OperationAck applyOperation(String documentId, String userId, DocumentOperation operation);
}

final class Document {
    public final String documentId;
    public final String ownerId;
    public final String title;
    public final int version;

    Document(String documentId, String ownerId, String title, int version) {
        this.documentId = documentId;
        this.ownerId = ownerId;
        this.title = title;
        this.version = version;
    }
}

final class DocumentOperation {
    public final String operationId;
    public final int baseVersion;
    public final String payload;

    DocumentOperation(String operationId, int baseVersion, String payload) {
        this.operationId = operationId;
        this.baseVersion = baseVersion;
        this.payload = payload;
    }
}

final class OperationAck {
    public final String operationId;
    public final int appliedVersion;
    public final boolean rebased;

    OperationAck(String operationId, int appliedVersion, boolean rebased) {
        this.operationId = operationId;
        this.appliedVersion = appliedVersion;
        this.rebased = rebased;
    }
}
