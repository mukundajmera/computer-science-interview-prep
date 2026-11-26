import pytest
from decimal import Decimal
import sys
import os

# To allow importing from python/v1-basic without issue
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from double_entry_ledger import DoubleEntryLedger
from digital_wallet_service import TccTransactionCoordinator, DigitalWalletService, Status

@pytest.fixture
def service():
    ledger = DoubleEntryLedger()
    coordinator = TccTransactionCoordinator()
    return DigitalWalletService(ledger, coordinator)

def test_transfer_double_entry_balance(service: DigitalWalletService):
    service.create_account("A", "USD", Decimal("100.00"))
    service.create_account("B", "USD", Decimal("50.00"))

    status = service.transfer("A", "B", Decimal("25.00"), "USD", "tx-1")
    
    assert status == Status.SUCCESS
    assert service.get_account("A").balance == Decimal("75.00")
    assert service.get_account("B").balance == Decimal("75.00")
    assert service.get_account("A").held_balance == Decimal("0.00")
    assert len(service.ledger.get_journal()) >= 2

def test_idempotency_key_duplicate_handling(service: DigitalWalletService):
    service.create_account("A", "USD", Decimal("100.00"))
    service.create_account("B", "USD", Decimal("50.00"))

    status1 = service.transfer("A", "B", Decimal("20.00"), "USD", "tx-2")
    status2 = service.transfer("A", "B", Decimal("20.00"), "USD", "tx-2")
    
    assert status1 == Status.SUCCESS
    assert status2 == Status.SUCCESS
    assert service.get_account("A").balance == Decimal("80.00")
    assert service.get_account("B").balance == Decimal("70.00")

def test_compensation_rollback_on_failure(service: DigitalWalletService):
    service.create_account("A", "USD", Decimal("10.00"))
    service.create_account("B", "USD", Decimal("50.00"))

    status = service.transfer("A", "B", Decimal("20.00"), "USD", "tx-3")
    
    assert status == Status.FAILED
    assert service.get_account("A").balance == Decimal("10.00")
    assert service.get_account("B").balance == Decimal("50.00")

def test_tcc_hold_and_confirm(service: DigitalWalletService):
    service.create_account("A", "USD", Decimal("100.00"))
    service.create_account("B", "USD", Decimal("50.00"))

    service.simulate_out_of_order_cancel("tx-4")

    status = service.transfer("A", "B", Decimal("30.00"), "USD", "tx-4")
    
    assert status == Status.FAILED
    assert service.get_account("A").balance == Decimal("100.00")
    assert service.get_account("B").balance == Decimal("50.00")

def test_event_log_replay(service: DigitalWalletService):
    service.create_account("A", "USD", Decimal("100.00"))
    service.create_account("B", "USD", Decimal("50.00"))

    service.transfer("A", "B", Decimal("40.00"), "USD", "tx-5")
    service.transfer("B", "A", Decimal("10.00"), "USD", "tx-6")

    assert service.get_account("A").balance == Decimal("70.00")
    assert service.get_account("B").balance == Decimal("80.00")

    # Manually mess up balances
    service.get_account("A").balance = Decimal("999.00")
    service.get_account("B").balance = Decimal("-50.00")

    service.replay_event_sourcing_history()

    # Should reconstruct to exact correct balance
    assert service.get_account("A").balance == Decimal("70.00")
    assert service.get_account("B").balance == Decimal("80.00")
