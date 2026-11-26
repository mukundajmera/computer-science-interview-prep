import uuid
import time
from typing import List, Dict, Optional
from threading import Lock
import copy
from thread_aggregator import ThreadAggregator

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


class EmailService:
    def __init__(self, spam_keywords: Optional[List[str]] = None):
        self.user_mailboxes: Dict[str, Mailbox] = {}
        self.spam_keywords = [kw.lower() for kw in (spam_keywords or [])]
        self._lock = Lock()

    def get_mailbox(self, user_id: str) -> Mailbox:
        with self._lock:
            if user_id not in self.user_mailboxes:
                self.user_mailboxes[user_id] = Mailbox(user_id)
            return self.user_mailboxes[user_id]

    def send_email(self, sender_id: str, message: EmailMessage):
        sender_mailbox = self.get_mailbox(sender_id)
        
        # Deep copy for sender
        sender_copy = copy.deepcopy(message)
        sender_copy.mark_as_read()
        sender_mailbox.add_message("Sent", sender_copy)

        all_recipients = set(message.to_recipients + message.cc_recipients + message.bcc_recipients)
        for recipient_id in all_recipients:
            recipient_copy = copy.deepcopy(message)
            self.receive_email(recipient_id, recipient_copy)

    def receive_email(self, recipient_id: str, message: EmailMessage):
        recipient_mailbox = self.get_mailbox(recipient_id)
        if self.is_spam(message):
            recipient_mailbox.add_message("Spam", message)
        else:
            recipient_mailbox.add_message("Inbox", message)

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
