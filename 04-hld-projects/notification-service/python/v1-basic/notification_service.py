"""
Notification Service - V1 Basic

Core notification service implementation in Python.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from abc import ABC, abstractmethod
from enum import Enum
import uuid
import re


class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationPriority(Enum):
    CRITICAL = "critical"  # < 1 second SLA
    HIGH = "high"          # < 30 seconds SLA
    NORMAL = "normal"      # < 5 minutes SLA
    LOW = "low"            # < 1 hour SLA


class NotificationStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"


@dataclass
class SendNotificationRequest:
    """Request to send a notification."""
    user_id: str
    template_id: str
    channel: NotificationChannel
    variables: Dict[str, str] = field(default_factory=dict)
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    idempotency_key: Optional[str] = None


@dataclass
class SendNotificationResponse:
    """Response after sending notification."""
    notification_id: str
    status: NotificationStatus
    estimated_delivery: Optional[datetime] = None


@dataclass
class Notification:
    """Notification entity."""
    notification_id: str
    user_id: str
    template_id: str
    channel: NotificationChannel
    priority: NotificationPriority
    variables: Dict[str, str]
    rendered_content: str
    status: NotificationStatus = NotificationStatus.QUEUED
    created_at: datetime = field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    attempt_count: int = 0
    last_error: Optional[str] = None
    
    @staticmethod
    def create(user_id: str, template_id: str, channel: NotificationChannel,
               priority: NotificationPriority, variables: Dict[str, str],
               rendered_content: str) -> 'Notification':
        return Notification(
            notification_id=str(uuid.uuid4()),
            user_id=user_id,
            template_id=template_id,
            channel=channel,
            priority=priority,
            variables=variables,
            rendered_content=rendered_content
        )
    
    def mark_sent(self):
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.utcnow()
    
    def mark_delivered(self):
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = datetime.utcnow()
    
    def mark_failed(self, error: str):
        self.status = NotificationStatus.FAILED
        self.last_error = error
    
    def increment_attempt(self):
        self.attempt_count += 1


@dataclass
class NotificationTemplate:
    """Template for notifications."""
    template_id: str
    channel: NotificationChannel
    name: str
    subject: Optional[str]  # For email
    body: str
    required_variables: List[str] = field(default_factory=list)
    version: int = 1
    is_active: bool = True


@dataclass
class UserPreferences:
    """User notification preferences."""
    user_id: str
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    device_tokens: List[str] = field(default_factory=list)
    
    def is_channel_enabled(self, channel: NotificationChannel) -> bool:
        channel_map = {
            NotificationChannel.EMAIL: self.email_enabled,
            NotificationChannel.SMS: self.sms_enabled,
            NotificationChannel.PUSH: self.push_enabled
        }
        return channel_map.get(channel, False)


class NotificationService(ABC):
    """Main notification service interface."""
    
    @abstractmethod
    def send(self, request: SendNotificationRequest) -> SendNotificationResponse:
        """Send a notification."""
        pass
    
    @abstractmethod
    def get_status(self, notification_id: str) -> Optional[Notification]:
        """Get notification status."""
        pass
    
    @abstractmethod
    def cancel(self, notification_id: str) -> bool:
        """Cancel a scheduled notification."""
        pass


class TemplateRenderer:
    """Template renderer for variable substitution."""
    
    VARIABLE_PATTERN = re.compile(r'\{\{\s*(\w+)\s*\}\}')
    
    def render(self, template: NotificationTemplate, 
               variables: Dict[str, str]) -> 'RenderedContent':
        # Validate required variables
        for required in template.required_variables:
            if required not in variables:
                raise ValueError(f"Missing required variable: {required}")
        
        rendered_subject = self._substitute(template.subject, variables)
        rendered_body = self._substitute(template.body, variables)
        
        return RenderedContent(subject=rendered_subject, body=rendered_body)
    
    def _substitute(self, text: Optional[str], 
                   variables: Dict[str, str]) -> Optional[str]:
        if text is None:
            return None
        
        def replace(match):
            var_name = match.group(1)
            return variables.get(var_name, '')
        
        return self.VARIABLE_PATTERN.sub(replace, text)


@dataclass
class RenderedContent:
    """Rendered content after variable substitution."""
    subject: Optional[str]
    body: str


@dataclass
class ProviderResult:
    """Result of sending via a provider."""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    
    @staticmethod
    def ok(message_id: str) -> 'ProviderResult':
        return ProviderResult(success=True, message_id=message_id)
    
    @staticmethod
    def failure(error: str) -> 'ProviderResult':
        return ProviderResult(success=False, error_message=error)


class ChannelProvider(ABC):
    """Interface for notification channel providers."""
    
    @abstractmethod
    def send(self, notification: Notification, 
             preferences: UserPreferences) -> ProviderResult:
        """Send a notification via this channel."""
        pass
    
    @abstractmethod
    def get_channel(self) -> NotificationChannel:
        """Get the channel this provider handles."""
        pass
    
    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if provider is healthy."""
        pass


class EmailProvider(ChannelProvider):
    """Email provider implementation (simulated)."""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self._healthy = True
    
    def send(self, notification: Notification, 
             preferences: UserPreferences) -> ProviderResult:
        email = preferences.email_address
        
        if not email:
            return ProviderResult.failure("No email address configured")
        
        print(f"[{self.provider_name}] Sending email to: {email}")
        print(f"  Content: {notification.rendered_content[:50]}...")
        
        message_id = f"msg-{uuid.uuid4().hex[:8]}"
        return ProviderResult.ok(message_id)
    
    def get_channel(self) -> NotificationChannel:
        return NotificationChannel.EMAIL
    
    def is_healthy(self) -> bool:
        return self._healthy


class SmsProvider(ChannelProvider):
    """SMS provider implementation (simulated)."""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self._healthy = True
    
    def send(self, notification: Notification,
             preferences: UserPreferences) -> ProviderResult:
        phone = preferences.phone_number
        
        if not phone:
            return ProviderResult.failure("No phone number configured")
        
        print(f"[{self.provider_name}] Sending SMS to: {phone}")
        
        message_id = f"sms-{uuid.uuid4().hex[:8]}"
        return ProviderResult.ok(message_id)
    
    def get_channel(self) -> NotificationChannel:
        return NotificationChannel.SMS
    
    def is_healthy(self) -> bool:
        return self._healthy


class PushProvider(ChannelProvider):
    """Push notification provider implementation (simulated)."""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self._healthy = True
    
    def send(self, notification: Notification,
             preferences: UserPreferences) -> ProviderResult:
        tokens = preferences.device_tokens
        
        if not tokens:
            return ProviderResult.failure("No device tokens registered")
        
        for token in tokens:
            print(f"[{self.provider_name}] Sending push to: {token[:10]}...")
        
        message_id = f"push-{uuid.uuid4().hex[:8]}"
        return ProviderResult.ok(message_id)
    
    def get_channel(self) -> NotificationChannel:
        return NotificationChannel.PUSH
    
    def is_healthy(self) -> bool:
        return self._healthy


class ChannelRouter:
    """Channel router that selects appropriate provider."""
    
    def __init__(self):
        self._providers: Dict[NotificationChannel, List[ChannelProvider]] = {}
    
    def register_provider(self, provider: ChannelProvider):
        channel = provider.get_channel()
        if channel not in self._providers:
            self._providers[channel] = []
        self._providers[channel].append(provider)
    
    def get_provider(self, channel: NotificationChannel) -> ChannelProvider:
        providers = self._providers.get(channel, [])
        
        if not providers:
            raise ValueError(f"No providers for channel: {channel}")
        
        for provider in providers:
            if provider.is_healthy():
                return provider
        
        return providers[0]
