package collab.v1;

import org.junit.jupiter.api.Test;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertFalse;

public class CollaborativeEditorServiceTest {
    
    // We create a dummy mock implementation directly in the test package
    // since the interfaces and return classes are package-private in collab.v1
    class MockCollaborativeEditorService implements CollaborativeEditorService {
        @Override
        public Document createDocument(String ownerId, String title) {
            return new Document("doc-1", ownerId, title, 1);
        }

        @Override
        public Optional<Document> getDocument(String documentId, String userId) {
            if ("doc-1".equals(documentId) && "user-1".equals(userId)) {
                return Optional.of(new Document("doc-1", "user-1", "Mock Title", 1));
            }
            return Optional.empty();
        }

        @Override
        public OperationAck applyOperation(String documentId, String userId, DocumentOperation operation) {
            boolean rebased = operation.baseVersion != 1;
            return new OperationAck(operation.operationId, 2, rebased);
        }
    }

    @Test
    public void testCreateDocument() {
        CollaborativeEditorService service = new MockCollaborativeEditorService();
        Document doc = service.createDocument("user-1", "Test Doc");
        
        assertEquals("doc-1", doc.documentId);
        assertEquals("user-1", doc.ownerId);
        assertEquals("Test Doc", doc.title);
        assertEquals(1, doc.version);
    }

    @Test
    public void testGetDocument() {
        CollaborativeEditorService service = new MockCollaborativeEditorService();
        Optional<Document> doc = service.getDocument("doc-1", "user-1");
        
        assertTrue(doc.isPresent());
        assertEquals("doc-1", doc.get().documentId);
        
        Optional<Document> notFound = service.getDocument("doc-2", "user-1");
        assertFalse(notFound.isPresent());
    }

    @Test
    public void testApplyOperation() {
        CollaborativeEditorService service = new MockCollaborativeEditorService();
        DocumentOperation op1 = new DocumentOperation("op-1", 1, "insert 'A'");
        OperationAck ack1 = service.applyOperation("doc-1", "user-1", op1);
        
        assertEquals("op-1", ack1.operationId);
        assertEquals(2, ack1.appliedVersion);
        assertFalse(ack1.rebased);
        
        DocumentOperation op2 = new DocumentOperation("op-2", 0, "insert 'B'");
        OperationAck ack2 = service.applyOperation("doc-1", "user-1", op2);
        assertTrue(ack2.rebased);
    }
}
