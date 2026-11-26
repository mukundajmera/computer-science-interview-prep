"""
Factory Method Pattern - V1 Basic (Classic Implementation)

Defines an interface for creating objects, but lets subclasses
decide which class to instantiate.
"""

from abc import ABC, abstractmethod


# Product interface
class Notification(ABC):
    """Abstract product interface."""
    
    @abstractmethod
    def send(self, message: str) -> None:
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        pass


# Concrete Products
class EmailNotification(Notification):
    """Email notification implementation."""
    
    def __init__(self, recipient: str):
        self.recipient = recipient
    
    def send(self, message: str) -> None:
        print(f"Sending EMAIL to {self.recipient}: {message}")
    
    def get_type(self) -> str:
        return "EMAIL"


class SMSNotification(Notification):
    """SMS notification implementation."""
    
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
    
    def send(self, message: str) -> None:
        print(f"Sending SMS to {self.phone_number}: {message}")
    
    def get_type(self) -> str:
        return "SMS"


class PushNotification(Notification):
    """Push notification implementation."""
    
    def __init__(self, device_token: str):
        self.device_token = device_token
    
    def send(self, message: str) -> None:
        print(f"Sending PUSH to device {self.device_token}: {message}")
    
    def get_type(self) -> str:
        return "PUSH"


# Creator (Abstract)
class NotificationCreator(ABC):
    """Abstract creator class."""
    
    @abstractmethod
    def create_notification(self, target: str) -> Notification:
        """Factory method - subclasses must implement."""
        pass
    
    def notify_user(self, target: str, message: str) -> None:
        """Template method using factory method."""
        notification = self.create_notification(target)
        print(f"Created {notification.get_type()} notification")
        notification.send(message)


# Concrete Creators
class EmailNotificationCreator(NotificationCreator):
    """Creates email notifications."""
    
    def create_notification(self, target: str) -> Notification:
        return EmailNotification(target)


class SMSNotificationCreator(NotificationCreator):
    """Creates SMS notifications."""
    
    def create_notification(self, target: str) -> Notification:
        return SMSNotification(target)


class PushNotificationCreator(NotificationCreator):
    """Creates push notifications."""
    
    def create_notification(self, target: str) -> Notification:
        return PushNotification(target)


# Demo
if __name__ == "__main__":
    print("=== Factory Method Pattern Demo ===\n")
    
    # Client code works with creators through abstract interface
    email_creator = EmailNotificationCreator()
    sms_creator = SMSNotificationCreator()
    push_creator = PushNotificationCreator()
    
    # Send notifications - client doesn't know concrete types
    email_creator.notify_user("user@example.com", "Welcome to our app!")
    print()
    
    sms_creator.notify_user("+1234567890", "Your OTP is 123456")
    print()
    
    push_creator.notify_user("device-token-abc", "You have a new message")
    
    print("\n=== Demonstrating Polymorphism ===\n")
    
    # Can swap creators without changing client code
    creators = [email_creator, sms_creator, push_creator]
    
    for creator in creators:
        creator.notify_user("target", "Broadcast message")
