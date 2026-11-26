from datetime import datetime, timezone
import re
from typing import List, Dict, Optional, Tuple, Set

class ModerationStatus:
    PASS = "PASS"
    FLAGGED = "FLAGGED"
    BLOCKED = "BLOCKED"
    NEEDS_REVIEW = "NEEDS_REVIEW"

class ContentEvent:
    def __init__(self, content_id: str, author_id: str, text: str, created_at: Optional[datetime] = None):
        self.content_id = content_id
        self.author_id = author_id
        self.text = text
        self.created_at = created_at if created_at else datetime.now(timezone.utc)

class ModerationResult:
    def __init__(self, content_id: str, status: str, reason: str, confidence: float = 1.0):
        self.content_id = content_id
        self.status = status
        self.reason = reason
        self.confidence = confidence
        self.decided_at = datetime.now(timezone.utc)

class ReviewItem:
    def __init__(self, event: ContentEvent, reason: str, confidence: float):
        self.event = event
        self.reason = reason
        self.confidence = confidence
        self.reviewer_decisions = [] # True for pass, False for block

class MLModelService:
    def predict(self, text: str) -> Tuple[bool, float, str]:
        # returns is_harmful, confidence, category
        pass

class ScaledContentModerationService:
    def __init__(self,
                 blocklist: List[str],
                 flag_patterns: List[str],
                 ml_service: MLModelService,
                 ml_timeout_ms: int = 200,
                 review_consensus_threshold: int = 2,
                 max_queue_size: int = 10000):
        self.blocklist = set(w.lower() for w in blocklist) if blocklist else set()
        self.flag_patterns = [re.compile(p) for p in flag_patterns] if flag_patterns else []
        self.ml_service = ml_service
        self.ml_timeout_ms = ml_timeout_ms
        self.review_consensus_threshold = review_consensus_threshold
        self.max_queue_size = max_queue_size

        self.review_queue: Dict[str, ReviewItem] = {}
        self.audit_log: List[ModerationResult] = []

    def evaluate_content(self, event: ContentEvent) -> ModerationResult:
        text_lower = event.text.lower()

        # Tier 1: Fast heuristic check
        for word in self.blocklist:
            if word in text_lower:
                return self._record_decision(event.content_id, ModerationStatus.BLOCKED, f"Blocked keyword: {word}", 1.0)

        for pattern in self.flag_patterns:
            if pattern.search(event.text):
                return self._enqueue_review(event, f"Flagged by pattern: {pattern.pattern}", 1.0)

        # Tier 2: ML Model Inference
        try:
            is_harmful, confidence, category = self.ml_service.predict(event.text)

            if is_harmful:
                if confidence > 0.9:
                    return self._record_decision(event.content_id, ModerationStatus.BLOCKED, f"ML blocked: {category}", confidence)
                elif confidence > 0.6:
                    return self._enqueue_review(event, f"ML flagged: {category}", confidence)
                else:
                    return self._record_decision(event.content_id, ModerationStatus.PASS, "ML low confidence harmful", confidence)
            else:
                return self._record_decision(event.content_id, ModerationStatus.PASS, "ML passed", confidence)
        except Exception as e:
            # Degraded mode fallback: Allow if ML fails/times out, but queue for async backfill or log
            # For simplicity, we PASS in degraded mode to avoid blocking benign content
            return self._record_decision(event.content_id, ModerationStatus.PASS, f"Degraded mode: {str(e)}", 0.0)

    def _enqueue_review(self, event: ContentEvent, reason: str, confidence: float) -> ModerationResult:
        if len(self.review_queue) >= self.max_queue_size:
            # Queue backpressure handling: degrade gracefully by failing open (PASS) or blocking depending on policy.
            # Here we choose to PASS to avoid outage or we could return a specific status. Let's PASS with degraded reason.
            return self._record_decision(event.content_id, ModerationStatus.PASS, f"Queue full, degraded: {reason}", confidence)

        self.review_queue[event.content_id] = ReviewItem(event, reason, confidence)
        return self._record_decision(event.content_id, ModerationStatus.NEEDS_REVIEW, reason, confidence)

    def _record_decision(self, content_id: str, status: str, reason: str, confidence: float) -> ModerationResult:
        result = ModerationResult(content_id, status, reason, confidence)
        self.audit_log.append(result)
        return result

    def process_review(self, content_id: str, approved: bool) -> Optional[ModerationResult]:
        if content_id not in self.review_queue:
            raise ValueError(f"Content {content_id} not found in review queue")

        item = self.review_queue[content_id]
        item.reviewer_decisions.append(approved)

        # Consensus check
        approvals = sum(1 for d in item.reviewer_decisions if d)
        rejections = sum(1 for d in item.reviewer_decisions if not d)

        if approvals >= self.review_consensus_threshold:
            del self.review_queue[content_id]
            return self._record_decision(content_id, ModerationStatus.PASS, "Appeals consensus: approved", 1.0)
        elif rejections >= self.review_consensus_threshold:
            del self.review_queue[content_id]
            return self._record_decision(content_id, ModerationStatus.BLOCKED, "Appeals consensus: rejected", 1.0)

        # Still needs more reviews
        return None

    def get_review_queue(self) -> List[ContentEvent]:
        return [item.event for item in self.review_queue.values()]
