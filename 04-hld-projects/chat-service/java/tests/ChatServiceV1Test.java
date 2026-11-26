package chatservice.v1;

import org.junit.jupiter.api.Test;
import java.util.UUID;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class ChatServiceV1Test {
    
    // In-memory repositories for testing
    static class InMemoryConversationRepository implements ConversationRepository {
        private final java.util.Map<UUID, Conversation> conversations = new java.util.HashMap<>();
        
        @Override
        public Conversation save(Conversation conversation) {
            conversations.put(conversation.getConversationId(), conversation);
            return conversation;
        }
        
        @Override
        public Conversation findById(UUID conversationId) {
            return conversations.get(conversationId);
        }
        
        @Override
        public List<Conversation> findByUserId(UUID userId) {
            return conversations.values().stream()
                .filter(c -> c.getParticipantIds().contains(userId))
                .collect(java.util.stream.Collectors.toList());
        }
        
        @Override
        public boolean isParticipant(UUID conversationId, UUID userId) {
            Conversation c = conversations.get(conversationId);
            return c != null && c.getParticipantIds().contains(userId);
        }
    }

    @Test
    void testBasicConversationServiceCreate() {
        ConversationRepository repo = new InMemoryConversationRepository();
        BasicConversationService service = new BasicConversationService(repo);
        
        UUID user1 = UUID.randomUUID();
        UUID user2 = UUID.randomUUID();
        
        Conversation conv = service.createDirectConversation(user1, user2);
        
        assertNotNull(conv);
        assertEquals("direct", conv.getType());
        assertEquals(2, conv.getParticipantIds().size());
        assertTrue(conv.getParticipantIds().contains(user1));
        assertTrue(conv.getParticipantIds().contains(user2));
        
        List<Conversation> user1Convs = service.getConversations(user1);
        assertEquals(1, user1Convs.size());
        assertEquals(conv.getConversationId(), user1Convs.get(0).getConversationId());
    }
}
