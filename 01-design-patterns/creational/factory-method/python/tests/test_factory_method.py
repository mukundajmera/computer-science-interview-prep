import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v1-basic"))
from factory_method import (
    EmailNotificationCreator,
    SMSNotificationCreator,
    PushNotificationCreator,
    EmailNotification,
    SMSNotification,
    PushNotification,
)


def test_email_notification_creation():
    creator = EmailNotificationCreator()
    notification = creator.create_notification("user@test.com")
    assert isinstance(notification, EmailNotification)
    assert notification.get_type() == "EMAIL"
    notification.send("Hello Email")


def test_sms_notification_creation():
    creator = SMSNotificationCreator()
    notification = creator.create_notification("+1234567890")
    assert isinstance(notification, SMSNotification)
    assert notification.get_type() == "SMS"
    notification.send("Hello SMS")


def test_push_notification_creation_and_notify_user():
    creator = PushNotificationCreator()
    notification = creator.create_notification("token_xyz")
    assert isinstance(notification, PushNotification)
    assert notification.get_type() == "PUSH"
    creator.notify_user("token_xyz", "Alert notification")
