import time
from enum import Enum
from typing import Dict, List, Any, Optional

class RemediationAction(Enum):
    PASS = "PASS"
    CHALLENGE_CAPTCHA = "CHALLENGE_CAPTCHA"
    BLOCK = "BLOCK"

class BotRiskResponse:
    def __init__(self, risk_score: float, confidence: float, action: RemediationAction, reasons: List[str], policy_version: str, queued_for_investigation: bool):
        self.risk_score = risk_score
        self.confidence = confidence
        self.action = action
        self.reasons = reasons
        self.policy_version = policy_version
        self.queued_for_investigation = queued_for_investigation

class Event:
    def __init__(self, account_id: str, action: str, context: Optional[Dict[str, Any]], timestamp: int):
        self.account_id = account_id
        self.action = action
        self.context = context if context is not None else {}
        self.timestamp = timestamp

class InvestigationTask:
    def __init__(self, account_id: str, risk_score: float, reasons: List[str], timestamp: int):
        self.account_id = account_id
        self.risk_score = risk_score
        self.reasons = reasons
        self.timestamp = timestamp

class BotDetectionPlatformService:
    def __init__(self):
        self.account_events: Dict[str, List[Event]] = {}
        self.investigation_queue: List[InvestigationTask] = []
        self.ip_reputation_scores: Dict[str, float] = {}

    def set_ip_reputation(self, ip: str, score: float):
        self.ip_reputation_scores[ip] = score

    def ingest_event(self, event: Event):
        if event.account_id not in self.account_events:
            self.account_events[event.account_id] = []
        self.account_events[event.account_id].append(event)

    def evaluate(self, current_event: Event) -> BotRiskResponse:
        self.ingest_event(current_event)

        history = self.account_events.get(current_event.account_id, [])
        now = current_event.timestamp

        one_minute_ago = now - 60000
        recent_events_count = sum(1 for e in history if e.timestamp >= one_minute_ago)
        velocity_score = min(1.0, recent_events_count / 50.0)

        ip = current_event.context.get("ip", "")
        ip_rep_score = self.ip_reputation_scores.get(ip, 0.0)

        device_id = current_event.context.get("device_id", "")
        if not device_id:
            device_entropy_score = 0.8
        elif len(device_id) < 5:
            device_entropy_score = 0.5
        else:
            device_entropy_score = 0.1

        risk_score = (velocity_score * 0.3) + (ip_rep_score * 0.6) + (device_entropy_score * 0.1)
        risk_score = min(1.0, max(0.0, risk_score))

        confidence = 0.5 + (min(len(history), 100) / 200.0)

        reasons = []
        if velocity_score > 0.6:
            reasons.append("velocity_spike")
        if ip_rep_score > 0.6:
            reasons.append("bad_ip_reputation")
        if device_entropy_score > 0.6:
            reasons.append("device_anomaly")

        queue_for_investigation = False
        if risk_score >= 0.8:
            action = RemediationAction.BLOCK
        elif risk_score >= 0.5:
            action = RemediationAction.CHALLENGE_CAPTCHA
            queue_for_investigation = True
        else:
            action = RemediationAction.PASS

        if queue_for_investigation:
            self.investigation_queue.append(InvestigationTask(
                current_event.account_id, risk_score, reasons, now
            ))

        return BotRiskResponse(
            risk_score,
            confidence,
            action,
            reasons,
            "v1-basic-policy",
            queue_for_investigation
        )

    def get_investigation_queue(self) -> List[InvestigationTask]:
        return list(self.investigation_queue)
