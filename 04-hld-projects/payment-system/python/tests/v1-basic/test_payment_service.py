import pytest
import sys
import os

# Add the parent directory to sys.path to allow importing payment_service
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))
from payment_service import PaymentService, PaymentState, TransactionType

@pytest.fixture
def payment_service():
    return PaymentService()

def test_create_payment_intent_idempotency(payment_service):
    idempotency_key = "key-123"
    intent1 = payment_service.create_payment_intent(idempotency_key, "m_1", "c_1", 1000, "USD")
    assert intent1 is not None
    assert intent1.state == PaymentState.CREATED

    intent2 = payment_service.create_payment_intent(idempotency_key, "m_1", "c_1", 1000, "USD")
    assert intent1.id == intent2.id  # Same intent returned

    with pytest.raises(ValueError, match="duplicate_idempotency_key"):
        payment_service.create_payment_intent(idempotency_key, "m_2", "c_2", 2000, "EUR")

def test_state_transitions(payment_service):
    intent = payment_service.create_payment_intent("key-1", "m_1", "c_1", 1000, "USD")

    auth_txn = payment_service.authorize(intent.id)
    assert auth_txn.type == TransactionType.AUTHORIZE
    assert payment_service.get_intent(intent.id).state == PaymentState.AUTHORIZED

    capture_txn = payment_service.capture(intent.id)
    assert capture_txn.type == TransactionType.CAPTURE
    assert payment_service.get_intent(intent.id).state == PaymentState.CAPTURED

def test_refund_logic(payment_service):
    intent = payment_service.create_payment_intent("key-1", "m_1", "c_1", 1000, "USD")
    payment_service.authorize(intent.id)
    payment_service.capture(intent.id)

    payment_service.refund(intent.id, 400)
    assert payment_service.get_intent(intent.id).state == PaymentState.PARTIALLY_REFUNDED

    payment_service.refund(intent.id, 600)
    assert payment_service.get_intent(intent.id).state == PaymentState.REFUNDED

    with pytest.raises(ValueError, match="invalid_state_transition"):
        payment_service.refund(intent.id, 100)

def test_ledger_balancing(payment_service):
    intent = payment_service.create_payment_intent("key-1", "m_1", "c_1", 1000, "USD")
    payment_service.authorize(intent.id)
    payment_service.capture(intent.id)

    ledger = payment_service.get_ledger()

    # Capture creates 2 entries (debit customer, credit merchant)
    assert len(ledger) == 2

    total_sum = sum(entry.amount for entry in ledger)
    assert total_sum == 0  # Double entry bookkeeping sum should be zero

    payment_service.refund(intent.id, 500)
    ledger = payment_service.get_ledger()

    # Refund creates 2 more entries (debit merchant, credit customer)
    assert len(ledger) == 4

    total_sum = sum(entry.amount for entry in ledger)
    assert total_sum == 0  # Still balances to zero

def test_void_payment(payment_service):
    intent = payment_service.create_payment_intent("key-1", "m_1", "c_1", 1000, "USD")
    payment_service.authorize(intent.id)
    payment_service.void_payment(intent.id)

    assert payment_service.get_intent(intent.id).state == PaymentState.VOIDED

    with pytest.raises(ValueError, match="invalid_state_transition"):
        payment_service.capture(intent.id)
