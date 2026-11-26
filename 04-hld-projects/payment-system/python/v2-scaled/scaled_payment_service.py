import time
import math
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

class WebhookType(Enum):
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

@dataclass
class WebhookEvent:
    event_id: str
    intent_id: str
    event_type: WebhookType
    payload_hash: str
    timestamp: float

class PaymentState(Enum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

@dataclass
class PaymentIntent:
    id: str
    amount: int
    state: PaymentState
    gateway_ref: Optional[str] = None
    seen_events: set = field(default_factory=set)

class ScaledPaymentService:
    def __init__(self):
        self.intents: Dict[str, PaymentIntent] = {}
        self.processed_webhooks: set = set()
        self.dead_letter_queue: List[Dict[str, Any]] = []
        # Store future state if we receive out-of-order events
        # key: intent_id, value: max priority state
        self.out_of_order_states: Dict[str, WebhookType] = {}

    def create_intent(self, intent_id: str, amount: int) -> PaymentIntent:
        if intent_id in self.intents:
            raise ValueError("Intent already exists")
        intent = PaymentIntent(id=intent_id, amount=amount, state=PaymentState.CREATED)
        self.intents[intent_id] = intent
        return intent

    def handle_webhook(self, event: WebhookEvent) -> bool:
        """
        Returns True if processed, False if duplicate.
        """
        if event.event_id in self.processed_webhooks:
            return False

        self.processed_webhooks.add(event.event_id)

        intent = self.intents.get(event.intent_id)
        if not intent:
            # We don't have the intent yet, stash state
            self.out_of_order_states[event.intent_id] = event.event_type
            return True

        self._apply_event_type(intent, event.event_type)
        return True

    def _apply_event_type(self, intent: PaymentIntent, event_type: WebhookType):
        state_priority = {
            PaymentState.CREATED: 0,
            PaymentState.PROCESSING: 1,
            PaymentState.AUTHORIZED: 2,
            PaymentState.CAPTURED: 3,
            PaymentState.REFUNDED: 4,
            PaymentState.FAILED: 5
        }

        event_to_state = {
            WebhookType.AUTHORIZED: PaymentState.AUTHORIZED,
            WebhookType.CAPTURED: PaymentState.CAPTURED,
            WebhookType.REFUNDED: PaymentState.REFUNDED,
            WebhookType.FAILED: PaymentState.FAILED
        }

        target_state = event_to_state[event_type]
        if state_priority[target_state] > state_priority[intent.state]:
            intent.state = target_state

    def reconcile_settlement_job(self, gateway_ref: str, expected_amount: int, fail_count: int = 0):
        # find intent
        target_intent = None
        for intent in self.intents.values():
            if intent.gateway_ref == gateway_ref:
                target_intent = intent
                break

        if not target_intent or target_intent.amount != expected_amount:
            # send to DLQ with exponential backoff
            backoff_sec = math.pow(2, fail_count)
            self.dead_letter_queue.append({
                "gateway_ref": gateway_ref,
                "expected_amount": expected_amount,
                "fail_count": fail_count + 1,
                "next_retry_at": time.time() + backoff_sec
            })
            return False

        if target_intent.state != PaymentState.CAPTURED:
             # reconcile
             target_intent.state = PaymentState.CAPTURED

        return True

    def process_dlq(self):
        now = time.time()
        to_process = [job for job in self.dead_letter_queue if job["next_retry_at"] <= now]
        self.dead_letter_queue = [job for job in self.dead_letter_queue if job["next_retry_at"] > now]

        for job in to_process:
            self.reconcile_settlement_job(
                job["gateway_ref"],
                job["expected_amount"],
                job["fail_count"]
            )
