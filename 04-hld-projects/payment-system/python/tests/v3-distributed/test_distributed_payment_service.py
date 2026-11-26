import uuid
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))
from distributed_payment_service import DistributedPaymentService, PaymentState, TransactionType

@pytest.fixture
def service():
    return DistributedPaymentService("us-east-1")

def test_successful_authorization_and_capture(service):
    idem_key = str(uuid.uuid4())
    intent = service.create_or_confirm_intent(idem_key, "merch1", "cust1", 1000, "USD")

    assert intent["state"] == PaymentState.AUTHORIZED

    capture_txn = service.capture(intent["id"])
    assert capture_txn["type"] == TransactionType.CAPTURE

    updated_intent = service.get_intent(intent["id"])
    assert updated_intent["state"] == PaymentState.CAPTURED

def test_idempotent_retries(service):
    idem_key = str(uuid.uuid4())

    first_intent = service.create_or_confirm_intent(idem_key, "merch1", "cust1", 1000, "USD")
    second_intent = service.create_or_confirm_intent(idem_key, "merch1", "cust1", 1000, "USD")

    assert first_intent["id"] == second_intent["id"]

    with pytest.raises(ValueError, match="duplicate_idempotency_key"):
        service.create_or_confirm_intent(idem_key, "merch1", "cust1", 2000, "USD")

def test_degraded_mode_async_authorization(service):
    service.set_degraded_mode(True)
    idem_key = str(uuid.uuid4())

    intent = service.create_or_confirm_intent(idem_key, "merch1", "cust1", 1000, "USD")
    assert intent["state"] == PaymentState.PROCESSING

    service.handle_provider_webhook(intent["id"], "SUCCESS")

    updated_intent = service.get_intent(intent["id"])
    assert updated_intent["state"] == PaymentState.AUTHORIZED

def test_distributed_saga_compensation(service):
    success_saga = service.execute_transfer_saga("acc1", "acc2", 500)
    assert not success_saga["compensated"]
    assert len(success_saga["steps_completed"]) == 2

    with pytest.raises(RuntimeError, match="Saga aborted and compensated"):
        service.execute_transfer_saga("acc1", "fail_acc2", 500)
