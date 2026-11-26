import re
import time
from enum import Enum
from typing import List, Optional, Dict, Any


class Action(Enum):
    ALLOW = "allow"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    AUTO_REMOVE = "auto_remove"


class ModerationRequest:
    def __init__(self, content_id: str, text: Optional[str] = None, media_refs: Optional[List[str]] = None, surface: Optional[str] = None):
        self.content_id = content_id
        self.text = text
        self.media_refs = media_refs or []
        self.surface = surface


class ModerationResponse:
    def __init__(self, risk_score: float, confidence: float, action: Action, reasons: List[str], policy_version: str):
        self.risk_score = risk_score
        self.confidence = confidence
        self.action = action
        self.reasons = reasons
        self.policy_version = policy_version


class AuditRecord:
    def __init__(self, content_id: str, initial_decision: ModerationResponse, final_action: Action, decided_at: float):
        self.content_id = content_id
        self.initial_decision = initial_decision
        self.final_action = final_action
        self.decided_at = decided_at


class ContentModerationPlatformService:
    def __init__(self, blocklist_keywords: Optional[List[str]] = None, warning_keywords: Optional[List[str]] = None, regex_patterns: Optional[List[str]] = None):
        self.blocklist_keywords = blocklist_keywords or []
        self.warning_keywords = warning_keywords or []
        self.blocklist_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in (regex_patterns or [])]
        self.audit_ledger: List[AuditRecord] = []
        self.current_policy_version = "p1.0"

    def evaluate(self, request: ModerationRequest) -> ModerationResponse:
        reasons = []
        risk_score = 0.0
        confidence = 1.0

        if request.text:
            lower_text = request.text.lower()

            for keyword in self.blocklist_keywords:
                if keyword.lower() in lower_text:
                    reasons.append(f"blocklist_keyword_match: {keyword}")
                    risk_score += 0.8

            for pattern in self.blocklist_patterns:
                if pattern.search(request.text):
                    reasons.append(f"regex_match: {pattern.pattern}")
                    risk_score += 0.8

            for keyword in self.warning_keywords:
                if keyword.lower() in lower_text:
                    reasons.append(f"warning_keyword_match: {keyword}")
                    risk_score += 0.4

        if request.media_refs:
            reasons.append("media_present")
            risk_score += 0.1
            confidence -= 0.1

        risk_score = min(risk_score, 1.0)

        if risk_score >= 0.8:
            action = Action.AUTO_REMOVE
        elif risk_score >= 0.4:
            action = Action.ESCALATE_TO_HUMAN
        else:
            action = Action.ALLOW

        response = ModerationResponse(risk_score, confidence, action, reasons, self.current_policy_version)

        self.audit_ledger.append(AuditRecord(
            content_id=request.content_id,
            initial_decision=response,
            final_action=action,
            decided_at=time.time()
        ))

        return response

    def record_moderator_decision(self, content_id: str, final_action: Action) -> None:
        for record in self.audit_ledger:
            if record.content_id == content_id:
                record.final_action = final_action
                record.decided_at = time.time()

    def get_audit_ledger(self) -> List[AuditRecord]:
        return list(self.audit_ledger)
