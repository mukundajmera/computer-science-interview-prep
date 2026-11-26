from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Optional, Any

class RiskState(Enum):
    ACTIVE = "ACTIVE"
    CHALLENGED = "CHALLENGED"
    LIMITED = "LIMITED"
    SUSPENDED = "SUSPENDED"

class ActionType(Enum):
    NONE = "NONE"
    CHALLENGE = "CHALLENGE"
    LIMIT = "LIMIT"
    SUSPEND = "SUSPEND"
    RESTORE = "RESTORE"

@dataclass
class BehaviorSignal:
    account_id: str
    signal_type: str
    signal_value: float
    event_time: datetime

@dataclass
class AccountRiskState:
    account_id: str
    score: float
    confidence: float
    state: RiskState
    policy_version: str
    model_version: str
    updated_at: datetime

@dataclass
class ActionEvent:
    account_id: str
    action: ActionType
    reason_code: str
    issued_at: datetime
    policy_version: str
    model_version: str
    rollback_ref: Optional[str] = None

@dataclass
class InvestigatorLabel:
    account_id: str
    label: str
    quality: float
    created_at: datetime

class BotDetectionService:
    def __init__(self):
        self.accounts: Dict[str, AccountRiskState] = {}
        self.action_history: List[ActionEvent] = []
        self.labels: List[InvestigatorLabel] = []
        self.appeals: List[Dict[str, Any]] = []

    def _calculate_score(self, signals: List[BehaviorSignal]) -> float:
        if not signals:
            return 0.0

        score = 0.0
        for signal in signals:
            if signal.signal_type == "failed_logins":
                score += signal.signal_value * 10
            elif signal.signal_type == "rapid_messages":
                score += signal.signal_value * 5
            elif signal.signal_type == "bot_signature":
                score += signal.signal_value * 50
        return min(100.0, score)

    def evaluate_account(self, account_id: str, signals: List[BehaviorSignal]) -> AccountRiskState:
        score = self._calculate_score(signals)
        confidence = 0.8 if len(signals) > 2 else 0.5

        state = RiskState.ACTIVE
        action = ActionType.NONE
        reason_code = "normal_behavior"

        if score >= 90:
            state = RiskState.SUSPENDED
            action = ActionType.SUSPEND
            reason_code = "high_risk_score"
        elif score >= 70:
            state = RiskState.LIMITED
            action = ActionType.LIMIT
            reason_code = "medium_high_risk_score"
        elif score >= 50:
            state = RiskState.CHALLENGED
            action = ActionType.CHALLENGE
            reason_code = "medium_risk_score"

        now = datetime.now(timezone.utc)
        risk_state = AccountRiskState(
            account_id=account_id,
            score=score,
            confidence=confidence,
            state=state,
            policy_version="v1",
            model_version="v1",
            updated_at=now
        )
        self.accounts[account_id] = risk_state

        if action != ActionType.NONE:
            action_event = ActionEvent(
                account_id=account_id,
                action=action,
                reason_code=reason_code,
                issued_at=now,
                policy_version="v1",
                model_version="v1"
            )
            self.action_history.append(action_event)

        return risk_state

    def submit_appeal(self, account_id: str, reason: str) -> bool:
        if account_id not in self.accounts:
            return False

        self.appeals.append({
            "account_id": account_id,
            "reason": reason,
            "submitted_at": datetime.now(timezone.utc),
            "status": "pending"
        })
        return True

    def submit_investigator_label(self, account_id: str, label: str, quality: float) -> InvestigatorLabel:
        label_record = InvestigatorLabel(
            account_id=account_id,
            label=label,
            quality=quality,
            created_at=datetime.now(timezone.utc)
        )
        self.labels.append(label_record)

        if label == "legitimate" and account_id in self.accounts:
            self.accounts[account_id].state = RiskState.ACTIVE
            self.accounts[account_id].score = 0.0
            self.accounts[account_id].updated_at = datetime.now(timezone.utc)

            action_event = ActionEvent(
                account_id=account_id,
                action=ActionType.RESTORE,
                reason_code="investigator_override",
                issued_at=datetime.now(timezone.utc),
                policy_version="v1",
                model_version="v1"
            )
            self.action_history.append(action_event)

        return label_record

    def get_account_status(self, account_id: str) -> Optional[AccountRiskState]:
        return self.accounts.get(account_id)

    def get_metrics(self, window_hours: int = 24) -> Dict[str, int]:
        metrics = {
            "total_evaluated": len(self.accounts),
            "suspended": 0,
            "limited": 0,
            "challenged": 0,
            "active": 0,
            "appeals_pending": len([a for a in self.appeals if a["status"] == "pending"])
        }

        for state in self.accounts.values():
            if state.state == RiskState.SUSPENDED:
                metrics["suspended"] += 1
            elif state.state == RiskState.LIMITED:
                metrics["limited"] += 1
            elif state.state == RiskState.CHALLENGED:
                metrics["challenged"] += 1
            elif state.state == RiskState.ACTIVE:
                metrics["active"] += 1

        return metrics
