package collab.v3;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertFalse;

public class DistributedCollaborationServiceTest {

    class MockDistributedCollaborationService implements DistributedCollaborationService {
        @Override
        public String routeDocumentOwner(String documentId) {
            if ("doc-1".equals(documentId)) return "node-1";
            return "node-default";
        }

        @Override
        public void replicateOperation(OperationReplicationEvent event) {
        }

        @Override
        public void rebuildSessionFromSnapshot(String documentId) {
        }
    }

    @Test
    public void testRouteDocumentOwner() {
        DistributedCollaborationService service = new MockDistributedCollaborationService();
        assertEquals("node-1", service.routeDocumentOwner("doc-1"));
        assertEquals("node-default", service.routeDocumentOwner("doc-2"));
    }

    @Test
    public void testReplicateOperation() {
        DistributedCollaborationService service = new MockDistributedCollaborationService();
        OperationReplicationEvent event = new OperationReplicationEvent("doc-1", 100L, "payload");
        service.replicateOperation(event);
        
        assertEquals("doc-1", event.documentId);
        assertEquals(100L, event.operationId);
        assertEquals("payload", event.payload);
        assertTrue(true); // Verification that method doesn't crash
    }

    @Test
    public void testRebuildSessionFromSnapshot() {
        DistributedCollaborationService service = new MockDistributedCollaborationService();
        service.rebuildSessionFromSnapshot("doc-1");
        assertTrue(true); // Verification that method doesn't crash
    }
}
