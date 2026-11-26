"""
Chat Service - v1-basic (Python)

Basic implementation with:
- One-on-one messaging
- Simple WebSocket connections
- Direct message storage and retrieval
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
import uuid


# ============================================================================
# DTOs / Entities
# ============================================================================

@dataclass
class Message:
    """A chat message."""
    message_id: str
    conversation_id: str
    sender_id: str
    content: str
    message_type: str = "text"
    reply_to_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Conversation:
    """A conversation between users."""
    conversation_id: str
    type: str  # "direct" or "group"
    name: Optional[str] = None
    participant_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SendMessageRequest:
    """Request to send a message."""
    conversation_id: str
    content: str
    message_type: str = "text"
    reply_to_id: Optional[str] = None


@dataclass
class MessageResponse:
    """Response after sending a message."""
    message_id: str
    status: str
    timestamp: datetime


# ============================================================================
# Repository Interfaces
# ============================================================================

class MessageRepository(ABC):
    """Repository for message persistence."""
    
    @abstractmethod
    def save(self, message: Message) -> Message:
        pass
    
    @abstractmethod
    def find_by_conversation_id(
        self, 
        conversation_id: str, 
        limit: int = 50, 
        before_message_id: Optional[str] = None
    ) -> List[Message]:
        pass
    
    @abstractmethod
    def find_by_id(self, message_id: str) -> Optional[Message]:
        pass


class ConversationRepository(ABC):
    """Repository for conversation persistence."""
    
    @abstractmethod
    def save(self, conversation: Conversation) -> Conversation:
        pass
    
    @abstractmethod
    def find_by_id(self, conversation_id: str) -> Optional[Conversation]:
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: str) -> List[Conversation]:
        pass
    
    @abstractmethod
    def is_participant(self, conversation_id: str, user_id: str) -> bool:
        pass


# ============================================================================
# WebSocket Interfaces
# ============================================================================

@dataclass
class WebSocketSession:
    """Represents a WebSocket connection."""
    session_id: str
    user_id: str
    
    def send_message(self, payload: str) -> None:
        """Send message to client."""
        pass
    
    def is_open(self) -> bool:
        """Check if connection is still open."""
        return True


class WebSocketHandler(ABC):
    """Handler for WebSocket events."""
    
    @abstractmethod
    def on_connect(self, session: WebSocketSession) -> None:
        pass
    
    @abstractmethod
    def on_message(self, session: WebSocketSession, payload: str) -> None:
        pass
    
    @abstractmethod
    def on_disconnect(self, session: WebSocketSession) -> None:
        pass


# ============================================================================
# Message Service
# ============================================================================

class MessageService(ABC):
    """Interface for message operations."""
    
    @abstractmethod
    def send_message(
        self, sender_id: str, request: SendMessageRequest
    ) -> MessageResponse:
        pass
    
    @abstractmethod
    def get_messages(
        self, 
        user_id: str, 
        conversation_id: str, 
        limit: int = 50,
        before: Optional[str] = None
    ) -> List[Message]:
        pass
    
    @abstractmethod
    def mark_as_read(
        self, user_id: str, conversation_id: str, last_read_message_id: str
    ) -> None:
        pass


class BasicMessageService(MessageService):
    """Basic synchronous message service."""
    
    def __init__(
        self,
        message_repository: MessageRepository,
        conversation_repository: ConversationRepository,
        user_sessions: Dict[str, WebSocketSession]
    ):
        self.message_repository = message_repository
        self.conversation_repository = conversation_repository
        self.user_sessions = user_sessions
    
    def send_message(
        self, sender_id: str, request: SendMessageRequest
    ) -> MessageResponse:
        """Send a message and deliver to recipients."""
        
        # Validate user is participant
        if not self.conversation_repository.is_participant(
            request.conversation_id, sender_id
        ):
            raise ValueError("User is not a participant in this conversation")
        
        # Create and save message
        message = Message(
            message_id=str(uuid.uuid4()),
            conversation_id=request.conversation_id,
            sender_id=sender_id,
            content=request.content,
            message_type=request.message_type,
            reply_to_id=request.reply_to_id
        )
        
        self.message_repository.save(message)
        
        # Deliver to recipients
        self._deliver_message(message)
        
        return MessageResponse(
            message_id=message.message_id,
            status="sent",
            timestamp=message.created_at
        )
    
    def get_messages(
        self, 
        user_id: str, 
        conversation_id: str, 
        limit: int = 50,
        before: Optional[str] = None
    ) -> List[Message]:
        """Get conversation history."""
        
        # Validate access
        if not self.conversation_repository.is_participant(
            conversation_id, user_id
        ):
            raise ValueError("Access denied")
        
        return self.message_repository.find_by_conversation_id(
            conversation_id, limit, before
        )
    
    def mark_as_read(
        self, user_id: str, conversation_id: str, last_read_message_id: str
    ) -> None:
        """Mark messages as read."""
        # In v1, just acknowledge - no status tracking
        pass
    
    def _deliver_message(self, message: Message) -> None:
        """Deliver message to online recipients."""
        conversation = self.conversation_repository.find_by_id(
            message.conversation_id
        )
        
        if not conversation:
            return
        
        for participant_id in conversation.participant_ids:
            if participant_id != message.sender_id:
                session = self.user_sessions.get(participant_id)
                if session and session.is_open():
                    session.send_message(self._serialize_message(message))
    
    def _serialize_message(self, message: Message) -> str:
        """Serialize message for WebSocket delivery."""
        return (
            f'{{"type": "new_message", '
            f'"messageId": "{message.message_id}", '
            f'"conversationId": "{message.conversation_id}", '
            f'"senderId": "{message.sender_id}", '
            f'"content": "{message.content}"}}'
        )


# ============================================================================
# Conversation Service
# ============================================================================

class ConversationService(ABC):
    """Interface for conversation operations."""
    
    @abstractmethod
    def create_direct_conversation(
        self, user_id_1: str, user_id_2: str
    ) -> Conversation:
        pass
    
    @abstractmethod
    def get_conversations(self, user_id: str) -> List[Conversation]:
        pass


class BasicConversationService(ConversationService):
    """Basic conversation service."""
    
    def __init__(self, conversation_repository: ConversationRepository):
        self.conversation_repository = conversation_repository
    
    def create_direct_conversation(
        self, user_id_1: str, user_id_2: str
    ) -> Conversation:
        """Create a 1:1 conversation."""
        conversation = Conversation(
            conversation_id=str(uuid.uuid4()),
            type="direct",
            participant_ids=[user_id_1, user_id_2]
        )
        
        return self.conversation_repository.save(conversation)
    
    def get_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user."""
        return self.conversation_repository.find_by_user_id(user_id)


# ============================================================================
# Basic WebSocket Handler
# ============================================================================

class BasicWebSocketHandler(WebSocketHandler):
    """Handler for WebSocket connections."""
    
    def __init__(
        self,
        message_service: MessageService,
        sessions: Dict[str, WebSocketSession]
    ):
        self.message_service = message_service
        self.sessions = sessions
    
    def on_connect(self, session: WebSocketSession) -> None:
        """Handle new connection."""
        self.sessions[session.user_id] = session
        print(f"User connected: {session.user_id}")
    
    def on_message(self, session: WebSocketSession, payload: str) -> None:
        """Handle incoming message."""
        # Parse and route to appropriate handler
        if '"type": "send_message"' in payload:
            self._handle_send_message(session, payload)
        elif '"type": "typing"' in payload:
            self._handle_typing_indicator(session, payload)
        elif '"type": "read_ack"' in payload:
            self._handle_read_ack(session, payload)
    
    def on_disconnect(self, session: WebSocketSession) -> None:
        """Handle disconnection."""
        if session.user_id in self.sessions:
            del self.sessions[session.user_id]
        print(f"User disconnected: {session.user_id}")
    
    def _handle_send_message(
        self, session: WebSocketSession, payload: str
    ) -> None:
        """Process send_message event."""
        # In production: proper JSON parsing
        pass
    
    def _handle_typing_indicator(
        self, session: WebSocketSession, payload: str
    ) -> None:
        """Broadcast typing indicator."""
        # In production: parse and forward to conversation participants
        pass
    
    def _handle_read_ack(
        self, session: WebSocketSession, payload: str
    ) -> None:
        """Process read acknowledgment."""
        pass


# ============================================================================
# In-Memory Repository Implementations (for testing)
# ============================================================================

class InMemoryMessageRepository(MessageRepository):
    """In-memory message storage for testing."""
    
    def __init__(self):
        self._messages: Dict[str, Message] = {}
        self._by_conversation: Dict[str, List[str]] = {}
    
    def save(self, message: Message) -> Message:
        self._messages[message.message_id] = message
        
        if message.conversation_id not in self._by_conversation:
            self._by_conversation[message.conversation_id] = []
        self._by_conversation[message.conversation_id].append(message.message_id)
        
        return message
    
    def find_by_conversation_id(
        self, 
        conversation_id: str, 
        limit: int = 50, 
        before_message_id: Optional[str] = None
    ) -> List[Message]:
        message_ids = self._by_conversation.get(conversation_id, [])
        messages = [self._messages[mid] for mid in message_ids if mid in self._messages]
        
        # Sort by created_at descending
        messages.sort(key=lambda m: m.created_at, reverse=True)
        
        return messages[:limit]
    
    def find_by_id(self, message_id: str) -> Optional[Message]:
        return self._messages.get(message_id)


class InMemoryConversationRepository(ConversationRepository):
    """In-memory conversation storage for testing."""
    
    def __init__(self):
        self._conversations: Dict[str, Conversation] = {}
    
    def save(self, conversation: Conversation) -> Conversation:
        self._conversations[conversation.conversation_id] = conversation
        return conversation
    
    def find_by_id(self, conversation_id: str) -> Optional[Conversation]:
        return self._conversations.get(conversation_id)
    
    def find_by_user_id(self, user_id: str) -> List[Conversation]:
        return [
            conv for conv in self._conversations.values()
            if user_id in conv.participant_ids
        ]
    
    def is_participant(self, conversation_id: str, user_id: str) -> bool:
        conv = self._conversations.get(conversation_id)
        return conv is not None and user_id in conv.participant_ids
