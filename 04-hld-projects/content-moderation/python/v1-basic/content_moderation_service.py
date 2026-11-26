import re
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone

class ModerationStatus(Enum):
    PASS = "PASS"
    FLAGGED = "FLAGGED"
    BLOCKED = "BLOCKED"

@dataclass
class ContentEvent:
    content_id: str
    author_id: str
    text: str
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

@dataclass
class ModerationResult:
    content_id: str
    status: ModerationStatus
    reason: Optional[str] = None
    decided_at: Optional[datetime] = None

class ContentModerationService:
    def __init__(self, blocklist: Optional[List[str]] = None, flag_patterns: Optional[List[str]] = None):
        self.blocklist: Set[str] = set([w.lower() for w in (blocklist or [])])
        self.flag_patterns: List[re.Pattern] = [re.compile(p) for p in (flag_patterns or [])]
        self.review_queue: List[ContentEvent] = []
        self.audit_log: List[ModerationResult] = []

    def evaluate_content(self, event: ContentEvent) -> ModerationResult:
        """
        Evaluate a content event, apply text filters, automated scoring,
        and add to review queue if flagged.
        """
        text_lower = event.text.lower()

        # 1. Check for blocked keywords
        for word in self.blocklist:
            if word in text_lower:
                return self._record_decision(
                    event.content_id,
                    ModerationStatus.BLOCKED,
                    f"Blocked keyword: {word}"
                )

        # 2. Check for flagged patterns
        for pattern in self.flag_patterns:
            if pattern.search(event.text):
                self.review_queue.append(event)
                return self._record_decision(
                    event.content_id,
                    ModerationStatus.FLAGGED,
                    f"Flagged by pattern: {pattern.pattern}"
                )

        # 3. Default to PASS
        return self._record_decision(event.content_id, ModerationStatus.PASS)

    def _record_decision(self, content_id: str, status: ModerationStatus, reason: Optional[str] = None) -> ModerationResult:
        result = ModerationResult(
            content_id=content_id,
            status=status,
            reason=reason,
            decided_at=datetime.now(timezone.utc)
        )
        self.audit_log.append(result)
        return result

    def get_review_queue(self) -> List[ContentEvent]:
        """
        Get all items currently awaiting human review.
        """
        return list(self.review_queue)

    def process_review(self, content_id: str, approved: bool) -> ModerationResult:
        """
        Process a manual human review decision.
        """
        # Find the event in the queue
        event = next((e for e in self.review_queue if e.content_id == content_id), None)
        if not event:
            raise ValueError(f"Content {content_id} not found in review queue")

        # Remove from queue
        self.review_queue.remove(event)

        status = ModerationStatus.PASS if approved else ModerationStatus.BLOCKED
        reason = "Human review approved" if approved else "Human review rejected"

        return self._record_decision(content_id, status, reason)

    def get_audit_log(self) -> List[ModerationResult]:
        """
        Retrieve the audit log of all decisions.
        """
        return list(self.audit_log)
