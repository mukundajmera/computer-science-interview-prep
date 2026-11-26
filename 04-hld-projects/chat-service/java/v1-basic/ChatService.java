package chatservice.v1;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.time.Instant;

/**
 * Chat Service - v1-basic
 * 
 * Basic implementation with:
 * - One-on-one messaging
 * - Simple WebSocket connections
 * - Direct message storage and retrieval
 */

// ============================================================================
// DTOs / Entities
// ============================================================================

class Message {
    private final UUID messageId;
    private final UUID conversationId;
    private final UUID senderId;
    private final String content;
    private final String messageType;
    private final Instant createdAt;
    private final UUID replyToId;

    public Message(UUID messageId, UUID conversationId, UUID senderId, 
                   String content, String messageType, UUID replyToId) {
        this.messageId = messageId;
        this.conversationId = conversationId;
        this.senderId = senderId;
        this.content = content;
        this.messageType = messageType;
        this.createdAt = Instant.now();
        this.replyToId = replyToId;
    }

    // Getters
    public UUID getMessageId() { return messageId; }
    public UUID getConversationId() { return conversationId; }
    public UUID getSenderId() { return senderId; }
    public String getContent() { return content; }
    public String getMessageType() { return messageType; }
    public Instant getCreatedAt() { return createdAt; }
    public UUID getReplyToId() { return replyToId; }
}

class Conversation {
    private final UUID conversationId;
    private final String type;
    private final String name;
    private final List<UUID> participantIds;
    private final Instant createdAt;

    public Conversation(UUID conversationId, String type, String name, 
                        List<UUID> participantIds) {
        this.conversationId = conversationId;
        this.type = type;
        this.name = name;
        this.participantIds = participantIds;
        this.createdAt = Instant.now();
    }

    public UUID getConversationId() { return conversationId; }
    public String getType() { return type; }
    public String getName() { return name; }
    public List<UUID> getParticipantIds() { return participantIds; }
    public Instant getCreatedAt() { return createdAt; }
}

class SendMessageRequest {
    private final UUID conversationId;
    private final String content;
    private final String messageType;
    private final UUID replyToId;

    public SendMessageRequest(UUID conversationId, String content, 
                              String messageType, UUID replyToId) {
        this.conversationId = conversationId;
        this.content = content;
        this.messageType = messageType;
        this.replyToId = replyToId;
    }

    public UUID getConversationId() { return conversationId; }
    public String getContent() { return content; }
    public String getMessageType() { return messageType; }
    public UUID getReplyToId() { return replyToId; }
}

class MessageResponse {
    private final UUID messageId;
    private final String status;
    private final Instant timestamp;

    public MessageResponse(UUID messageId, String status, Instant timestamp) {
        this.messageId = messageId;
        this.status = status;
        this.timestamp = timestamp;
    }

    public UUID getMessageId() { return messageId; }
    public String getStatus() { return status; }
    public Instant getTimestamp() { return timestamp; }
}

// ============================================================================
// Repository Interfaces
// ============================================================================

interface MessageRepository {
    Message save(Message message);
    List<Message> findByConversationId(UUID conversationId, int limit, UUID beforeMessageId);
    Message findById(UUID messageId);
}

interface ConversationRepository {
    Conversation save(Conversation conversation);
    Conversation findById(UUID conversationId);
    List<Conversation> findByUserId(UUID userId);
    boolean isParticipant(UUID conversationId, UUID userId);
}

// ============================================================================
// WebSocket Handler Interface
// ============================================================================

interface WebSocketSession {
    String getSessionId();
    UUID getUserId();
    void sendMessage(String payload);
    boolean isOpen();
}

interface WebSocketHandler {
    void onConnect(WebSocketSession session);
    void onMessage(WebSocketSession session, String payload);
    void onDisconnect(WebSocketSession session);
}

// ============================================================================
// Message Service
// ============================================================================

interface MessageService {
    MessageResponse sendMessage(UUID senderId, SendMessageRequest request);
    List<Message> getMessages(UUID userId, UUID conversationId, int limit, UUID before);
    void markAsRead(UUID userId, UUID conversationId, UUID lastReadMessageId);
}

class BasicMessageService implements MessageService {
    private final MessageRepository messageRepository;
    private final ConversationRepository conversationRepository;
    private final Map<UUID, WebSocketSession> userSessions;

    public BasicMessageService(MessageRepository messageRepository,
                               ConversationRepository conversationRepository,
                               Map<UUID, WebSocketSession> userSessions) {
        this.messageRepository = messageRepository;
        this.conversationRepository = conversationRepository;
        this.userSessions = userSessions;
    }

    @Override
    public MessageResponse sendMessage(UUID senderId, SendMessageRequest request) {
        // Validate user is participant
        if (!conversationRepository.isParticipant(request.getConversationId(), senderId)) {
            throw new RuntimeException("User is not a participant in this conversation");
        }

        // Create and save message
        Message message = new Message(
            UUID.randomUUID(),
            request.getConversationId(),
            senderId,
            request.getContent(),
            request.getMessageType(),
            request.getReplyToId()
        );

        messageRepository.save(message);

        // Deliver to recipient (basic sync delivery)
        deliverMessage(message);

        return new MessageResponse(
            message.getMessageId(),
            "sent",
            message.getCreatedAt()
        );
    }

    @Override
    public List<Message> getMessages(UUID userId, UUID conversationId, 
                                      int limit, UUID before) {
        // Validate access
        if (!conversationRepository.isParticipant(conversationId, userId)) {
            throw new RuntimeException("Access denied");
        }

        return messageRepository.findByConversationId(conversationId, limit, before);
    }

    @Override
    public void markAsRead(UUID userId, UUID conversationId, UUID lastReadMessageId) {
        // In v1, just acknowledge - no status tracking
        // Would update last_read position in database
    }

    /**
     * Basic synchronous message delivery.
     * In production, this would be async via message queue.
     */
    private void deliverMessage(Message message) {
        Conversation conversation = conversationRepository.findById(
            message.getConversationId()
        );

        for (UUID participantId : conversation.getParticipantIds()) {
            if (!participantId.equals(message.getSenderId())) {
                WebSocketSession session = userSessions.get(participantId);
                if (session != null && session.isOpen()) {
                    // Would serialize message to JSON
                    session.sendMessage(serializeMessage(message));
                }
            }
        }
    }

    private String serializeMessage(Message message) {
        // Simplified JSON serialization
        return String.format(
            "{\"type\":\"new_message\",\"messageId\":\"%s\",\"content\":\"%s\"}",
            message.getMessageId(),
            message.getContent()
        );
    }
}

// ============================================================================
// Conversation Service
// ============================================================================

interface ConversationService {
    Conversation createDirectConversation(UUID userId1, UUID userId2);
    List<Conversation> getConversations(UUID userId);
}

class BasicConversationService implements ConversationService {
    private final ConversationRepository conversationRepository;

    public BasicConversationService(ConversationRepository conversationRepository) {
        this.conversationRepository = conversationRepository;
    }

    @Override
    public Conversation createDirectConversation(UUID userId1, UUID userId2) {
        Conversation conversation = new Conversation(
            UUID.randomUUID(),
            "direct",
            null,
            List.of(userId1, userId2)
        );

        return conversationRepository.save(conversation);
    }

    @Override
    public List<Conversation> getConversations(UUID userId) {
        return conversationRepository.findByUserId(userId);
    }
}

// ============================================================================
// Basic WebSocket Handler
// ============================================================================

class BasicWebSocketHandler implements WebSocketHandler {
    private final MessageService messageService;
    private final Map<UUID, WebSocketSession> sessions;

    public BasicWebSocketHandler(MessageService messageService,
                                  Map<UUID, WebSocketSession> sessions) {
        this.messageService = messageService;
        this.sessions = sessions;
    }

    @Override
    public void onConnect(WebSocketSession session) {
        sessions.put(session.getUserId(), session);
        System.out.println("User connected: " + session.getUserId());
    }

    @Override
    public void onMessage(WebSocketSession session, String payload) {
        // Parse incoming message and route to appropriate handler
        // In production: use proper JSON parsing
        if (payload.contains("\"type\":\"send_message\"")) {
            handleSendMessage(session, payload);
        } else if (payload.contains("\"type\":\"typing\"")) {
            handleTypingIndicator(session, payload);
        }
    }

    @Override
    public void onDisconnect(WebSocketSession session) {
        sessions.remove(session.getUserId());
        System.out.println("User disconnected: " + session.getUserId());
    }

    private void handleSendMessage(WebSocketSession session, String payload) {
        // Parse and process message
        // In production: proper JSON deserialization
    }

    private void handleTypingIndicator(WebSocketSession session, String payload) {
        // Broadcast typing indicator to other participants
    }
}
