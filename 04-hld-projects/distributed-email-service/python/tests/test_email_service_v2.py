import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from email_service import EmailService as V1EmailService, EmailMessage as V1EmailMessage
from email_service_v2 import (
    EmailService, EmailMessage, IngestionQueue, RateLimitExceededError,
)
from thread_aggregator_v2 import ThreadAggregator


class FakeClock:
    def __init__(self, start: float = 1_000_000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float):
        self.now += seconds


@pytest.fixture
def email_service():
    return EmailService(spam_keywords=["viagra", "lottery", "free money"])


# --- Parity tests: v2 must keep every v1 guarantee ---

def test_v1_still_works():
    v1 = V1EmailService(spam_keywords=["viagra"])
    msg = V1EmailMessage(sender="alice@demo.com", to_recipients=["bob@demo.com"], subject="Hi")
    v1.send_email("alice@demo.com", msg)
    assert len(v1.get_mailbox("bob@demo.com").get_messages_in_folder("Inbox")) == 1


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

    bob_mailbox.delete_message(msg.message_id)
    assert len(bob_mailbox.get_messages_in_folder("Inbox")) == 0
    assert len(bob_mailbox.get_messages_in_folder("Trash")) == 1

    spam_msg = EmailMessage(sender="eve@demo.com", to_recipients=["bob@demo.com"], subject="Win Free Money")
    email_service.send_email("eve@demo.com", spam_msg)

    assert len(bob_mailbox.get_messages_in_folder("Spam")) == 1
    assert bob_mailbox.get_messages_in_folder("Spam")[0].subject == "Win Free Money"


# --- v2 item 1: asynchronous, fail-closed inbound ingestion ---

def test_inbound_enqueue_then_process(email_service):
    msg = EmailMessage(sender="ext@yahoo.example", to_recipients=["bob@demo.com"], subject="External")
    accepted = email_service.receive_email_inbound("bob@demo.com", msg)
    assert accepted is True
    # Async: nothing delivered until the worker runs.
    bob_mailbox = email_service.get_mailbox("bob@demo.com")
    assert len(bob_mailbox.get_messages_in_folder("Inbox")) == 0
    assert email_service.ingestion_queue.depth() == 1

    delivered = email_service.process_pending()
    assert delivered == 1
    assert len(bob_mailbox.get_messages_in_folder("Inbox")) == 1
    assert email_service.ingestion_queue.depth() == 0


def test_inbound_fails_closed_when_queue_down(email_service):
    email_service.ingestion_queue.inject_failures(1)
    msg = EmailMessage(sender="ext@yahoo.example", to_recipients=["bob@demo.com"], subject="Retry me")
    accepted = email_service.receive_email_inbound("bob@demo.com", msg)
    # Transient 4xx: nothing accepted, nothing queued, sender will retry.
    assert accepted is False
    assert email_service.ingestion_queue.depth() == 0

    # The MTA's retry succeeds once the queue recovers.
    accepted_retry = email_service.receive_email_inbound("bob@demo.com", msg)
    assert accepted_retry is True
    assert email_service.process_pending() == 1
    assert len(email_service.get_mailbox("bob@demo.com").get_messages_in_folder("Inbox")) == 1


def test_inbound_spam_routed_after_processing(email_service):
    spam = EmailMessage(sender="eve@demo.com", to_recipients=["bob@demo.com"], subject="Win Free Money")
    assert email_service.receive_email_inbound("bob@demo.com", spam) is True
    # Not yet classified: spam routing happens in the async pipeline.
    assert len(email_service.get_mailbox("bob@demo.com").get_messages_in_folder("Spam")) == 0
    email_service.process_pending()
    assert len(email_service.get_mailbox("bob@demo.com").get_messages_in_folder("Spam")) == 1


def test_inbound_fifo_order_preserved(email_service):
    for i in range(3):
        email_service.receive_email_inbound("bob@demo.com", EmailMessage(
            sender="ext@demo.com", to_recipients=["bob@demo.com"], subject=f"m{i}"))
    email_service.process_pending()
    inbox = email_service.get_mailbox("bob@demo.com").get_messages_in_folder("Inbox")
    assert [m.subject for m in inbox] == ["m0", "m1", "m2"]


# --- v2 item 2: outbound rate limiting ---

def test_rate_limit_allows_within_window():
    clock = FakeClock()
    service = EmailService(max_sends_per_window=3, rate_window_seconds=60.0, clock=clock)
    for i in range(3):
        service.send_email("alice@demo.com", EmailMessage(
            sender="alice@demo.com", to_recipients=["bob@demo.com"], subject=f"n{i}"))
    assert len(service.get_mailbox("bob@demo.com").get_messages_in_folder("Inbox")) == 3


def test_rate_limit_blocks_over_limit():
    clock = FakeClock()
    service = EmailService(max_sends_per_window=2, rate_window_seconds=60.0, clock=clock)
    for i in range(2):
        service.send_email("alice@demo.com", EmailMessage(
            sender="alice@demo.com", to_recipients=["bob@demo.com"], subject=f"n{i}"))
    with pytest.raises(RateLimitExceededError):
        service.send_email("alice@demo.com", EmailMessage(
            sender="alice@demo.com", to_recipients=["bob@demo.com"], subject="n2"))
    # The rejected send delivered nothing, not even the Sent copy.
    assert len(service.get_mailbox("bob@demo.com").get_messages_in_folder("Inbox")) == 2
    assert len(service.get_mailbox("alice@demo.com").get_messages_in_folder("Sent")) == 2


def test_rate_limit_window_resets():
    clock = FakeClock()
    service = EmailService(max_sends_per_window=1, rate_window_seconds=60.0, clock=clock)
    service.send_email("alice@demo.com", EmailMessage(
        sender="alice@demo.com", to_recipients=["bob@demo.com"], subject="first"))
    with pytest.raises(RateLimitExceededError):
        service.send_email("alice@demo.com", EmailMessage(
            sender="alice@demo.com", to_recipients=["bob@demo.com"], subject="second"))
    clock.advance(61.0)
    service.send_email("alice@demo.com", EmailMessage(
        sender="alice@demo.com", to_recipients=["bob@demo.com"], subject="after window"))
    subjects = [m.subject for m in service.get_mailbox("bob@demo.com").get_messages_in_folder("Inbox")]
    assert subjects == ["first", "after window"]


def test_rate_limit_is_per_sender():
    clock = FakeClock()
    service = EmailService(max_sends_per_window=1, rate_window_seconds=60.0, clock=clock)
    service.send_email("alice@demo.com", EmailMessage(
        sender="alice@demo.com", to_recipients=["bob@demo.com"], subject="from alice"))
    # Bob's quota is independent of Alice's.
    service.send_email("bob@demo.com", EmailMessage(
        sender="bob@demo.com", to_recipients=["alice@demo.com"], subject="from bob"))
    assert len(service.get_mailbox("alice@demo.com").get_messages_in_folder("Inbox")) == 1


# --- v2 item 3: order-independent threading ---

def _msg(subject, ts, in_reply_to=None, references=None):
    m = EmailMessage(sender="x@demo.com", to_recipients=["y@demo.com"], subject=subject,
                     in_reply_to=in_reply_to, references=references)
    m.timestamp = ts
    return m


def test_threading_reply_arriving_before_parent():
    parent = _msg("Parent", ts=1.0)
    reply = _msg("Re: Parent", ts=2.0, in_reply_to=parent.message_id,
                 references=[parent.message_id])
    # v1 bug scenario: the reply appears BEFORE its parent in the list.
    threads = ThreadAggregator.group_messages_into_threads([reply, parent])
    assert len(threads) == 1
    assert [m.subject for m in threads[0]] == ["Parent", "Re: Parent"]


def test_threading_multi_level_chain_shuffled():
    m1 = _msg("Root", ts=1.0)
    m2 = _msg("Re: Root", ts=2.0, in_reply_to=m1.message_id, references=[m1.message_id])
    m3 = _msg("Re: Re: Root", ts=3.0, in_reply_to=m2.message_id,
              references=[m1.message_id, m2.message_id])
    threads = ThreadAggregator.group_messages_into_threads([m3, m1, m2])
    assert len(threads) == 1
    assert [m.subject for m in threads[0]] == ["Root", "Re: Root", "Re: Re: Root"]


def test_threading_cycle_in_headers_terminates():
    a = _msg("A", ts=1.0)
    b = _msg("B", ts=2.0, in_reply_to=a.message_id, references=[a.message_id])
    a.in_reply_to = b.message_id
    a.references = [b.message_id]
    threads = ThreadAggregator.group_messages_into_threads([a, b])
    assert len(threads) == 1
    assert len(threads[0]) == 2


def test_threading_unknown_reference_starts_new_thread():
    orphan = _msg("Orphan reply", ts=1.0, in_reply_to="missing@elsewhere",
                  references=["missing@elsewhere"])
    threads = ThreadAggregator.group_messages_into_threads([orphan])
    assert len(threads) == 1
    assert threads[0][0].subject == "Orphan reply"
