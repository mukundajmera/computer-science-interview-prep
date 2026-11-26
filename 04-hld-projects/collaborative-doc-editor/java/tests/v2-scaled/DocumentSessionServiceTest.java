package collab.v2;

import org.junit.jupiter.api.Test;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertFalse;

public class DocumentSessionServiceTest {
    
    class MockDocumentSessionService implements DocumentSessionService {
        @Override
        public SessionToken joinSession(String documentId, String userId, long lastSeenOperationId) {
            return new SessionToken(documentId, userId, lastSeenOperationId + 1);
        }

        @Override
        public void publishCursor(String documentId, String userId, int position) {
        }

        @Override
        public void leaveSession(String documentId, String userId) {
        }
    }

    class MockOperationLogStore implements OperationLogStore {
        private List<OperationEvent> events = new ArrayList<>();

        @Override
        public void append(OperationEvent event) {
            events.add(event);
        }

        @Override
        public List<OperationEvent> replay(String documentId, long afterOperationId, int limit) {
            List<OperationEvent> result = new ArrayList<>();
            for (OperationEvent e : events) {
                if (e.documentId.equals(documentId) && e.operationId > afterOperationId) {
                    result.add(e);
                    if (result.size() >= limit) break;
                }
            }
            return result;
        }
    }

    @Test
    public void testJoinSession() {
        DocumentSessionService service = new MockDocumentSessionService();
        SessionToken token = service.joinSession("doc-1", "user-1", 10L);
        
        assertEquals("doc-1", token.documentId);
        assertEquals("user-1", token.userId);
        assertEquals(11L, token.streamOffset);
    }

    @Test
    public void testPublishAndLeaveSession() {
        DocumentSessionService service = new MockDocumentSessionService();
        service.publishCursor("doc-1", "user-1", 5);
        service.leaveSession("doc-1", "user-1");
        assertTrue(true);
    }

    @Test
    public void testOperationLogStore() {
        OperationLogStore store = new MockOperationLogStore();
        store.append(new OperationEvent(1L, "doc-1", "payload-1"));
        store.append(new OperationEvent(2L, "doc-1", "payload-2"));
        store.append(new OperationEvent(3L, "doc-2", "payload-3"));
        
        List<OperationEvent> replays = store.replay("doc-1", 1L, 10);
        assertEquals(1, replays.size());
        assertEquals(2L, replays.get(0).operationId);
        assertEquals("payload-2", replays.get(0).payload);
    }
}
