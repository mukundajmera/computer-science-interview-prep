import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from email_service import EmailService, EmailMessage

@pytest.fixture
def email_service():
    return EmailService(spam_keywords=["viagra", "lottery", "free money"])

def test_send_and_inbox_delivery(email_service):
    msg = EmailMessage(
        sender="alice@demo.com",
        to_recipients=["bob@demo.com"],
        subject="Hello",
        body="How are you?"
    )
    email_service.send_email("alice@demo.com", msg)

    alice_mailbox = email_service.get_mailbox("alice@demo.com")
    assert len(alice_mailbox.get_messages_in_folder("Sent")) == 1

    bob_mailbox = email_service.get_mailbox("bob@demo.com")
    inbox = bob_mailbox.get_messages_in_folder("Inbox")
    assert len(inbox) == 1
    assert inbox[0].subject == "Hello"

def test_threading_via_in_reply_to(email_service):
    msg1 = EmailMessage(
        sender="alice@demo.com",
        to_recipients=["bob@demo.com"],
        subject="Project",
        body="Let's start"
    )
    email_service.send_email("alice@demo.com", msg1)

    msg2 = EmailMessage(
        sender="bob@demo.com",
        to_recipients=["alice@demo.com"],
        subject="Re: Project",
        body="Sure",
        in_reply_to=msg1.message_id,
        references=[msg1.message_id]
    )
    email_service.send_email("bob@demo.com", msg2)

    threads = email_service.get_conversations_in_folder("alice@demo.com", "Inbox")
    # Alice sent msg1 (in Sent), received msg2 (in Inbox)
    assert len(threads) == 1
    assert len(threads[0]) == 1
    assert threads[0][0].subject == "Re: Project"

def test_unread_count_tracking(email_service):
    msg1 = EmailMessage(sender="alice@demo.com", to_recipients=["bob@demo.com"], subject="S1")
    msg2 = EmailMessage(sender="alice@demo.com", to_recipients=["bob@demo.com"], subject="S2")
    
    email_service.send_email("alice@demo.com", msg1)
    email_service.send_email("alice@demo.com", msg2)

    bob_mailbox = email_service.get_mailbox("bob@demo.com")
    assert bob_mailbox.get_unread_count("Inbox") == 2

    received_msg1 = bob_mailbox.get_message_by_id(msg1.message_id)
    received_msg1.mark_as_read()
    assert bob_mailbox.get_unread_count("Inbox") == 1

def test_attachment_storage_pointer(email_service):
    msg = EmailMessage(
        sender="alice@demo.com",
        to_recipients=["bob@demo.com"],
        subject="Photos",
        body="See attached",
        attachment_references=["s3://bucket/photo1.jpg"]
    )
    email_service.send_email("alice@demo.com", msg)

    bob_mailbox = email_service.get_mailbox("bob@demo.com")
    received = bob_mailbox.get_messages_in_folder("Inbox")[0]
    
    assert len(received.attachment_references) == 1
    assert received.attachment_references[0] == "s3://bucket/photo1.jpg"

def test_folder_move_and_delete(email_service):
    msg = EmailMessage(sender="alice@demo.com", to_recipients=["bob@demo.com"], subject="Hello")
    email_service.send_email("alice@demo.com", msg)

    bob_mailbox = email_service.get_mailbox("bob@demo.com")
    assert len(bob_mailbox.get_messages_in_folder("Inbox")) == 1

    # Move to trash
    bob_mailbox.delete_message(msg.message_id)
    assert len(bob_mailbox.get_messages_in_folder("Inbox")) == 0
    assert len(bob_mailbox.get_messages_in_folder("Trash")) == 1

    # Test spam keyword classification as an extra check
    spam_msg = EmailMessage(sender="eve@demo.com", to_recipients=["bob@demo.com"], subject="Win Free Money")
    email_service.send_email("eve@demo.com", spam_msg)
    
    assert len(bob_mailbox.get_messages_in_folder("Spam")) == 1
    assert bob_mailbox.get_messages_in_folder("Spam")[0].subject == "Win Free Money"
