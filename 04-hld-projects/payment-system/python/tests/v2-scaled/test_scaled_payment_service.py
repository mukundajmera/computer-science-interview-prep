import pytest
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))
from scaled_payment_service import ScaledPaymentService, WebhookEvent, WebhookType, PaymentState

def test_webhook_deduplication():
    service = ScaledPaymentService()
    intent = service.create_intent("intent_1", 100)

    event = WebhookEvent("ev_1", "intent_1", WebhookType.AUTHORIZED, "hash", time.time())

    assert service.handle_webhook(event) is True
    assert intent.state == PaymentState.AUTHORIZED

    # duplicate
    assert service.handle_webhook(event) is False
    assert intent.state == PaymentState.AUTHORIZED

def test_out_of_order_webhook():
    service = ScaledPaymentService()
    intent = service.create_intent("intent_2", 200)

    # captured arrives before authorized
    ev_captured = WebhookEvent("ev_cap", "intent_2", WebhookType.CAPTURED, "hash", time.time())
    ev_authorized = WebhookEvent("ev_auth", "intent_2", WebhookType.AUTHORIZED, "hash", time.time())

    service.handle_webhook(ev_captured)
    assert intent.state == PaymentState.CAPTURED

    service.handle_webhook(ev_authorized)
    # should still be captured
    assert intent.state == PaymentState.CAPTURED

def test_dlq_exponential_backoff():
    service = ScaledPaymentService()
    # No intent created
    res = service.reconcile_settlement_job("ref_123", 500)
    assert res is False

    assert len(service.dead_letter_queue) == 1
    job = service.dead_letter_queue[0]
    assert job["fail_count"] == 1

    # Process DLQ before backoff
    time.sleep(0.1) # not enough
    service.process_dlq()
    assert len(service.dead_letter_queue) == 1

    # Emulate time pass
    job["next_retry_at"] = time.time() - 1
    service.process_dlq()
    assert len(service.dead_letter_queue) == 1
    assert service.dead_letter_queue[0]["fail_count"] == 2

def test_settlement_reconciliation():
    service = ScaledPaymentService()
    intent = service.create_intent("intent_3", 300)
    intent.gateway_ref = "ref_456"

    # Status mismatch
    intent.state = PaymentState.AUTHORIZED

    res = service.reconcile_settlement_job("ref_456", 300)
    assert res is True
    assert intent.state == PaymentState.CAPTURED
