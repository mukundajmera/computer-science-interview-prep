import time
import uuid
import heapq
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, Future
import threading

class Action(Enum):
    ALLOW = "allow"
    DEMOTE = "demote"
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

class Policy:
    def __init__(self, version: str, auto_remove_threshold: float, escalate_threshold: float, demote_threshold: float):
        self.version = version
        self.auto_remove_threshold = auto_remove_threshold
        self.escalate_threshold = escalate_threshold
        self.demote_threshold = demote_threshold

class ReviewTask:
    def __init__(self, content_id: str, priority: int):
        self.task_id = str(uuid.uuid4())
        self.content_id = content_id
        self.priority = priority
        self.created_at = time.time()
        self.reviewer_votes: Dict[str, Action] = {}
        self.resolved = False
        self.final_action: Optional[Action] = None

    def __lt__(self, other: 'ReviewTask'):
        if self.priority != other.priority:
            return self.priority > other.priority # Higher priority first
        return self.created_at < other.created_at # Older tasks first

class AuditRecord:
    def __init__(self, content_id: str, initial_decision: ModerationResponse, final_action: Action, decided_at: float):
        self.content_id = content_id
        self.initial_decision = initial_decision
        self.final_action = final_action
        self.decided_at = decided_at

class ModelResult:
    def __init__(self, score: float, confidence: float, reasons: List[str]):
        self.score = score
        self.confidence = confidence
        self.reasons = reasons

class ScaledContentModerationPlatformService:
    def __init__(self, initial_policy: Policy, max_workers: int = 4):
        self.active_policy = initial_policy
        self.policy_cache: Dict[str, Policy] = {initial_policy.version: initial_policy}
        self.review_queue: List[ReviewTask] = []
        self.queue_lock = threading.Lock()
        self.audit_ledger: List[AuditRecord] = []
        self.ledger_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_map: Dict[str, ReviewTask] = {}
        self.task_map_lock = threading.Lock()

    def update_policy(self, new_policy: Policy) -> None:
        self.policy_cache[new_policy.version] = new_policy
        self.active_policy = new_policy

    def rollback_policy(self, version: str) -> None:
        if version in self.policy_cache:
            self.active_policy = self.policy_cache[version]
        else:
            raise ValueError(f"Policy version not found in cache: {version}")

    def get_active_policy(self) -> Policy:
        return self.active_policy

    def _run_text_safety_model(self, text: Optional[str]) -> ModelResult:
        if not text:
            return ModelResult(0.0, 1.0, [])
        lower = text.lower()
        reasons = []
        score = 0.0
        conf = 0.9
        if "hate" in lower:
            score += 0.8
            reasons.append("hate_speech")
        if "spam" in lower:
            score += 0.5
            reasons.append("spam")
        return ModelResult(min(score, 1.0), conf, reasons)

    def _run_media_hash_check(self, media_refs: List[str]) -> ModelResult:
        if not media_refs:
            return ModelResult(0.0, 1.0, [])
        reasons = []
        score = 0.0
        conf = 0.8
        for ref in media_refs:
            if "bad" in ref:
                score += 0.9
                reasons.append("known_bad_media")
            else:
                score += 0.1
                reasons.append("unknown_media")
                conf -= 0.1
        return ModelResult(min(score, 1.0), max(0.1, conf), reasons)

    def evaluate_async(self, request: ModerationRequest) -> Future:
        policy = self.active_policy

        # Submit tasks concurrently
        text_future = self.executor.submit(self._run_text_safety_model, request.text)
        media_future = self.executor.submit(self._run_media_hash_check, request.media_refs)

        def combine_results():
            text_res = text_future.result()
            media_res = media_future.result()

            final_score = max(text_res.score, media_res.score)
            final_confidence = min(text_res.confidence, media_res.confidence)
            all_reasons = text_res.reasons + media_res.reasons

            priority = 0
            if final_score >= policy.auto_remove_threshold:
                action = Action.AUTO_REMOVE
            elif final_score >= policy.escalate_threshold:
                action = Action.ESCALATE_TO_HUMAN
                priority = int(final_score * 100)
            elif final_score >= policy.demote_threshold:
                action = Action.DEMOTE
            else:
                action = Action.ALLOW

            response = ModerationResponse(final_score, final_confidence, action, all_reasons, policy.version)

            with self.ledger_lock:
                self.audit_ledger.append(AuditRecord(request.content_id, response, action, time.time()))

            if action == Action.ESCALATE_TO_HUMAN:
                task = ReviewTask(request.content_id, priority)
                with self.queue_lock:
                    heapq.heappush(self.review_queue, task)
                with self.task_map_lock:
                    self.task_map[task.task_id] = task

            return response

        return self.executor.submit(combine_results)

    def get_next_review_task(self) -> Optional[ReviewTask]:
        with self.queue_lock:
            if self.review_queue:
                return heapq.heappop(self.review_queue)
            return None

    def submit_review_vote(self, task_id: str, reviewer_id: str, vote: Action, required_consensus_size: int) -> bool:
        with self.task_map_lock:
            task = self.task_map.get(task_id)

        if not task or task.resolved:
            return False

        # Properly synchronize updates using a shared lock (task_map_lock is easy, or add lock to ReviewTask)
        with self.task_map_lock:
            if task.resolved:
                return False
            task.reviewer_votes[reviewer_id] = vote

            if len(task.reviewer_votes) >= required_consensus_size:
                counts = {}
                for v in task.reviewer_votes.values():
                    counts[v] = counts.get(v, 0) + 1

                majority_action = Action.ESCALATE_TO_HUMAN
                max_votes = -1
                for act, count in counts.items():
                    if count > max_votes:
                        max_votes = count
                        majority_action = act

                task.final_action = majority_action
                task.resolved = True

                with self.ledger_lock:
                    for record in self.audit_ledger:
                        if record.content_id == task.content_id:
                            record.final_action = majority_action
                            record.decided_at = time.time()
                return True
        return False

    def get_audit_ledger(self) -> List[AuditRecord]:
        with self.ledger_lock:
            return list(self.audit_ledger)

    def shutdown(self):
        self.executor.shutdown(wait=True)
