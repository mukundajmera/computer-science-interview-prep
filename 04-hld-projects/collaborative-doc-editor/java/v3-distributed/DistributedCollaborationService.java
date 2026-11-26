package collab.v3;

public interface DistributedCollaborationService {
    String routeDocumentOwner(String documentId);
    void replicateOperation(OperationReplicationEvent event);
    void rebuildSessionFromSnapshot(String documentId);
}

final class OperationReplicationEvent {
    public final String documentId;
    public final long operationId;
    public final String payload;

    OperationReplicationEvent(String documentId, long operationId, String payload) {
        this.documentId = documentId;
        this.operationId = operationId;
        this.payload = payload;
    }
}
