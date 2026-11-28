"""v2-extended email service.

Improvements over v1-basic (named per the repo rule v1-basic -> v2-extended):
1. Asynchronous, fail-closed inbound ingestion (PITFALLS #3 + FOLLOW-UPS
   #3): external mail enters through receive_email_inbound(), which enqueues
   onto an IngestionQueue and acknowledges immediately (the "250 OK"); the
   async worker process_pending() applies spam classification and delivers.
   If the queue is unavailable the worker FAILS CLOSED: it returns False (a
   transient 4xx) and keeps nothing, so the sending MTA retries instead of
   the message being silently lost. A failure injection hook simulates the
   queue outage.
2. Outbound rate limiting (FOLLOW-UPS #2, spam and abuse prevention):
   configurable per-sender sends-per-window policy with an injectable
   clock; exceeding the window raises RateLimitExceededError before any
   delivery happens. Disabled by default (v1 parity).
3. Order-independent threading (PITFALLS #5): see thread_aggregator_v2.py.
"""

import uuid
import time
from typing import List, Dict, Optional, Tuple
from threading import Lock
import copy
try:
    from .thread_aggregator_v2 import ThreadAggregator
except ImportError:
    from thread_aggregator_v2 import ThreadAggregator


class RateLimitExceededError(Exception):
    """Raised when a sender exceeds the configured outbound rate limit."""


class QueueUnavailableError(Exception):
    """Internal: the ingestion queue rejected an enqueue (injected outage)."""


class EmailMessage:
    def __init__(self, sender: str, to_recipients: List[str], cc_recipients: Optional[List[str]] = None,
                 bcc_recipients: Optional[List[str]] = None, subject: str = "", body: str = "",
                 attachment_references: Optional[List[str]] = None, in_reply_to: Optional[str] = None,
                 references: Optional[List[str]] = None):
        self.message_id = f"{uuid.uuid4()}@distributed-email-service.com"
        self.sender = sender
        self.to_recipients = to_recipients or []
        self.cc_recipients = cc_recipients or []
        self.bcc_recipients = bcc_recipients or []
        self.subject = subject
        self.body = body
        self.attachment_references = attachment_references or []
        self.in_reply_to = in_reply_to
        self.references = references or []
        self.timestamp = time.time()
        self.is_read = False

    def mark_as_read(self):
        self.is_read = True

    def mark_as_unread(self):
        self.is_read = False


class Mailbox:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.folders: Dict[str, List[EmailMessage]] = {
            "Inbox": [],
            "Sent": [],
            "Drafts": [],
            "Trash": [],
            "Spam": []
        }
        self.message_folder_mapping: Dict[str, str] = {}
        self._lock = Lock()

    def add_message(self, folder_name: str, message: EmailMessage):
        with self._lock:
            if folder_name not in self.folders:
                self.folders[folder_name] = []
            self.folders[folder_name].append(message)
            self.message_folder_mapping[message.message_id] = folder_name

    def move_message(self, message_id: str, target_folder: str) -> bool:
        with self._lock:
            current_folder = self.message_folder_mapping.get(message_id)
            if not current_folder or current_folder == target_folder:
                return False

            if target_folder not in self.folders:
                self.folders[target_folder] = []

            for msg in self.folders[current_folder]:
                if msg.message_id == message_id:
                    self.folders[current_folder].remove(msg)
                    self.folders[target_folder].append(msg)
                    self.message_folder_mapping[message_id] = target_folder
                    return True
            return False

    def get_messages_in_folder(self, folder_name: str) -> List[EmailMessage]:
        with self._lock:
            return list(self.folders.get(folder_name, []))

    def get_unread_count(self, folder_name: str) -> int:
        with self._lock:
            messages = self.folders.get(folder_name, [])
            return sum(1 for msg in messages if not msg.is_read)

    def get_message_by_id(self, message_id: str) -> Optional[EmailMessage]:
        with self._lock:
            folder = self.message_folder_mapping.get(message_id)
            if folder:
                for msg in self.folders[folder]:
                    if msg.message_id == message_id:
                        return msg
            return None

    def delete_message(self, message_id: str):
        self.move_message(message_id, "Trash")


class IngestionQueue:
    """Simulated durable queue between the inbound SMTP worker and the
    async processing pipeline, with an outage injection hook (v2 item 1)."""

    def __init__(self):
        self._entries: List[Tuple[str, EmailMessage]] = []
        self._fail_next = 0
        self._lock = Lock()

    def inject_failures(self, count: int):
        with self._lock:
            self._fail_next = count

    def enqueue(self, recipient_id: str, message: EmailMessage):
        with self._lock:
            if self._fail_next > 0:
                self._fail_next -= 1
                raise QueueUnavailableError("simulated queue outage")
            self._entries.append((recipient_id, message))

    def drain(self) -> List[Tuple[str, EmailMessage]]:
        with self._lock:
            entries = list(self._entries)
            self._entries = []
            return entries

    def depth(self) -> int:
        with self._lock:
            return len(self._entries)


class EmailService:
    def __init__(self, spam_keywords: Optional[List[str]] = None,
                 max_sends_per_window: Optional[int] = None,
                 rate_window_seconds: float = 60.0, clock=None,
                 ingestion_queue: Optional[IngestionQueue] = None):
        if max_sends_per_window is not None and max_sends_per_window < 1:
            raise ValueError("max_sends_per_window must be positive or None")
        if rate_window_seconds <= 0:
            raise ValueError("rate_window_seconds must be positive")
        self.user_mailboxes: Dict[str, Mailbox] = {}
        self.spam_keywords = [kw.lower() for kw in (spam_keywords or [])]
        self.max_sends_per_window = max_sends_per_window
        self.rate_window_seconds = rate_window_seconds
        self._clock = clock if clock is not None else time.time
        self._send_timestamps: Dict[str, List[float]] = {}
        self.ingestion_queue = ingestion_queue if ingestion_queue is not None else IngestionQueue()
        self._lock = Lock()

    def get_mailbox(self, user_id: str) -> Mailbox:
        with self._lock:
            if user_id not in self.user_mailboxes:
                self.user_mailboxes[user_id] = Mailbox(user_id)
            return self.user_mailboxes[user_id]

    # --- outbound path (v2 item 2: per-sender rate limiting) ---

    def _check_rate_limit(self, sender_id: str):
        if self.max_sends_per_window is None:
            return
        now = self._clock()
        window_start = now - self.rate_window_seconds
        timestamps = [t for t in self._send_timestamps.get(sender_id, []) if t > window_start]
        if len(timestamps) >= self.max_sends_per_window:
            self._send_timestamps[sender_id] = timestamps
            raise RateLimitExceededError(
                f"sender {sender_id} exceeded {self.max_sends_per_window} sends per {self.rate_window_seconds}s window")
        timestamps.append(now)
        self._send_timestamps[sender_id] = timestamps

    def send_email(self, sender_id: str, message: EmailMessage):
        self._check_rate_limit(sender_id)

        sender_mailbox = self.get_mailbox(sender_id)

        sender_copy = copy.deepcopy(message)
        sender_copy.mark_as_read()
        sender_mailbox.add_message("Sent", sender_copy)

        all_recipients = set(message.to_recipients + message.cc_recipients + message.bcc_recipients)
        for recipient_id in all_recipients:
            recipient_copy = copy.deepcopy(message)
            self.receive_email(recipient_id, recipient_copy)

    # --- inbound paths ---

    def receive_email(self, recipient_id: str, message: EmailMessage):
        """Direct internal delivery (v1 parity, used by send_email)."""
        recipient_mailbox = self.get_mailbox(recipient_id)
        if self.is_spam(message):
            recipient_mailbox.add_message("Spam", message)
        else:
            recipient_mailbox.add_message("Inbox", message)

    def receive_email_inbound(self, recipient_id: str, message: EmailMessage) -> bool:
        """External SMTP ingestion (v2 item 1). Returns True on 250 OK:
        the message is durably queued and will be processed asynchronously.
        Returns False on transient failure (4xx): nothing was accepted, and
        the sending MTA is expected to retry, so failing closed loses
        nothing."""
        try:
            self.ingestion_queue.enqueue(recipient_id, message)
            return True
        except QueueUnavailableError:
            return False

    def process_pending(self) -> int:
        """Async worker: drain the ingestion queue and deliver. Returns the
        number of messages delivered."""
        delivered = 0
        for recipient_id, message in self.ingestion_queue.drain():
            self.receive_email(recipient_id, message)
            delivered += 1
        return delivered

    # --- classification, search, threading ---

    def is_spam(self, message: EmailMessage) -> bool:
        body_lower = message.body.lower()
        subject_lower = message.subject.lower()
        for kw in self.spam_keywords:
            if kw in body_lower or kw in subject_lower:
                return True
        return False

    def search_messages(self, user_id: str, query: str) -> List[EmailMessage]:
        mailbox = self.get_mailbox(user_id)
        results = []
        query_lower = query.lower()
        for folder in ["Inbox", "Sent", "Drafts"]:
            for msg in mailbox.get_messages_in_folder(folder):
                if query_lower in msg.subject.lower() or \
                   query_lower in msg.body.lower() or \
                   query_lower in msg.sender.lower():
                    results.append(msg)
        return results

    def get_conversations_in_folder(self, user_id: str, folder_name: str) -> List[List[EmailMessage]]:
        mailbox = self.get_mailbox(user_id)
        messages = mailbox.get_messages_in_folder(folder_name)
        return ThreadAggregator.group_messages_into_threads(messages)
