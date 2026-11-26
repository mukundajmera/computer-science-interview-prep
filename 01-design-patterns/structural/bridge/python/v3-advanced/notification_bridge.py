"""
Bridge Pattern - V3 Advanced: Notifications + Senders

Notification types define message policy while sender implementations define
delivery mechanics. Both dimensions can grow independently.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class DeliveryReceipt:
    channel: str
    recipient: str
    subject: str
    body: str
    priority: str


class MessageSender(ABC):
    """Implementation interface for delivery channels."""

    @abstractmethod
    def send(self, subject: str, body: str, priority: str) -> DeliveryReceipt:
        pass


class EmailSender(MessageSender):
    def __init__(self, address: str):
        self.address = address

    def send(self, subject: str, body: str, priority: str) -> DeliveryReceipt:
        return DeliveryReceipt("email", self.address, subject, body, priority)


class SmsSender(MessageSender):
    def __init__(self, phone_number: str):
        self.phone_number = phone_number

    def send(self, subject: str, body: str, priority: str) -> DeliveryReceipt:
        return DeliveryReceipt("sms", self.phone_number, subject, body, priority)


class InAppSender(MessageSender):
    def __init__(self, user_id: str):
        self.user_id = user_id

    def send(self, subject: str, body: str, priority: str) -> DeliveryReceipt:
        return DeliveryReceipt("in-app", self.user_id, subject, body, priority)


class Notification(ABC):
    """Abstraction for notification policy."""

    def __init__(self, sender: MessageSender):
        self._sender = sender

    def set_sender(self, sender: MessageSender) -> None:
        self._sender = sender

    @abstractmethod
    def notify(self, body: str, topic: str):
        pass


class UrgentNotification(Notification):
    def notify(self, body: str, topic: str) -> DeliveryReceipt:
        return self._sender.send(f"Urgent: {topic}", body, "HIGH")


class RoutineNotification(Notification):
    def notify(self, body: str, topic: str) -> DeliveryReceipt:
        return self._sender.send(f"Update: {topic}", body, "NORMAL")


class DigestNotification:
    """Refined abstraction that broadcasts one digest through many senders."""

    def __init__(self, senders: Iterable[MessageSender]):
        self._senders = list(senders)

    def notify(self, body: str, topic: str) -> List[DeliveryReceipt]:
        return [
            sender.send(f"Digest: {topic}", body, "LOW")
            for sender in self._senders
        ]


if __name__ == "__main__":
    notification = UrgentNotification(EmailSender("ops@example.com"))
    print(notification.notify("Database latency", "incident-7"))
    notification.set_sender(SmsSender("+15551234567"))
    print(notification.notify("Database latency", "incident-7"))
