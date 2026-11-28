import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../v1-basic'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../v2-extended'))

import pytest
from decimal import Decimal

from digital_wallet_service import DigitalWalletService as V1Service, TccTransactionCoordinator as V1Coordinator
from double_entry_ledger import DoubleEntryLedger as V1Ledger
from digital_wallet_service_v2 import DigitalWalletService, TccTransactionCoordinator
from double_entry_ledger_v2 import DoubleEntryLedger


class FakeClock:
    def __init__(self, start: float = 1_000_000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float):
        self.now += seconds


@pytest.fixture
def v1_wallet():
    ledger = V1Ledger()
    coordinator = V1Coordinator()
    service = V1Service(ledger, coordinator)
    service.create_account("A", "USD", Decimal('1000'))
    service.create_account("B", "USD", Decimal('500'))
    return service


@pytest.fixture
def wallet():
    ledger = DoubleEntryLedger()
    coordinator = TccTransactionCoordinator()
    service = DigitalWalletService(ledger, coordinator)
    service.create_account("A", "USD", Decimal('1000'))
    service.create_account("B", "USD", Decimal('500'))
    return service


# --- Parity tests: v2 must keep every v1 guarantee ---

def test_transfer_success(wallet):
    status = wallet.transfer("A", "B", Decimal('100'), "USD", "tx1")
    assert status.name == 'SUCCESS'
    assert wallet.get_account("A").balance == Decimal('900')
    assert wallet.get_account("B").balance == Decimal('600')


def test_idempotent_retry(wallet):
    status1 = wallet.transfer("A", "B", Decimal('100'), "USD", "tx1")
    status2 = wallet.transfer("A", "B", Decimal('100'), "USD", "tx1")
    assert status1.name == 'SUCCESS'
    assert status2.name == 'SUCCESS'
    assert wallet.get_account("A").balance == Decimal('900')
    assert wallet.get_account("B").balance == Decimal('600')


def test_insufficient_funds(wallet):
    status = wallet.transfer("A", "B", Decimal('10000'), "USD", "tx2")
    assert status.name == 'FAILED'
    assert wallet.get_account("A").balance == Decimal('1000')


def test_v1_out_of_order_cancel_flag(v1_wallet):
    # v1 known issue / behavior note: flag exists on the state
    v1_wallet.simulate_out_of_order_cancel("tx3")
    status = v1_wallet.transfer("A", "B", Decimal('100'), "USD", "tx3")
    assert status.name == 'FAILED'
    assert v1_wallet.get_account("A").balance == Decimal('1000')


def test_v2_out_of_order_cancel_flag(wallet):
    wallet.simulate_out_of_order_cancel("tx3")
    status = wallet.transfer("A", "B", Decimal('100'), "USD", "tx3")
    assert status.name == 'FAILED'
    assert wallet.get_account("A").balance == Decimal('1000')


def test_event_replay(wallet):
    wallet.transfer("A", "B", Decimal('100'), "USD", "tx4")
    wallet.get_account("A").balance = Decimal('0')  # Simulate data corruption/loss
    wallet.replay_event_sourcing_history()
    assert wallet.get_account("A").balance == Decimal('900')
    assert wallet.get_account("B").balance == Decimal('600')


# --- v2 item 1: transfer input validation ---

def test_negative_amount_rejected(wallet):
    with pytest.raises(ValueError):
        wallet.transfer("A", "B", Decimal('-100'), "USD", "tx-neg")
    assert wallet.get_account("A").balance == Decimal('1000')
    assert wallet.get_account("B").balance == Decimal('500')
    assert len(wallet.ledger.get_journal()) == 4  # only the account funding entries


def test_zero_amount_rejected(wallet):
    with pytest.raises(ValueError):
        wallet.transfer("A", "B", Decimal('0'), "USD", "tx-zero")


def test_same_account_rejected(wallet):
    with pytest.raises(ValueError):
        wallet.transfer("A", "A", Decimal('100'), "USD", "tx-same")


def test_missing_account_rejected(wallet):
    with pytest.raises(ValueError):
        wallet.transfer("A", "ZZZ", Decimal('100'), "USD", "tx-missing")


def test_currency_mismatch_rejected(wallet):
    wallet.create_account("C", "EUR", Decimal('100'))
    with pytest.raises(ValueError):
        wallet.transfer("A", "C", Decimal('50'), "USD", "tx-fx")


# --- v2 item 2: symmetrical TRY phase with failure injection ---

def test_destination_try_failure_cancels_safely(wallet):
    calls = []

    def failing_hook(dest, amount, currency):
        calls.append(dest.account_id)
        raise TimeoutError("destination shard unreachable")

    status = wallet.transfer("A", "B", Decimal('100'), "USD", "tx-dest-fail",
                             destination_try=failing_hook)
    assert status.name == 'FAILED'
    assert calls == ["B"]
    assert wallet.get_account("A").balance == Decimal('1000')
    assert wallet.get_account("A").held_balance == Decimal('0')
    assert wallet.get_account("B").balance == Decimal('500')
    # No ledger entries beyond account funding: no money moved at all.
    assert len(wallet.ledger.get_journal()) == 4


def test_destination_try_hook_called_before_confirm(wallet):
    order = []

    def observing_hook(dest, amount, currency):
        state = wallet.coordinator.get_state(
            wallet.idempotency_store["tx-order"][0])
        order.append((dest.account_id, state.phase.name))
        return True

    status = wallet.transfer("A", "B", Decimal('100'), "USD", "tx-order",
                             destination_try=observing_hook)
    assert status.name == 'SUCCESS'
    # Hook saw the destination while the transaction was still in TRY.
    assert order == [("B", "TRY")]


def test_failed_transfer_hold_fully_released(wallet):
    status = wallet.transfer("A", "B", Decimal('10000'), "USD", "tx-hold")
    assert status.name == 'FAILED'
    assert wallet.get_account("A").held_balance == Decimal('0')


# --- v2 item 3: expiring idempotency store ---

def test_duplicate_within_ttl_returns_cached():
    clock = FakeClock()
    service = DigitalWalletService(DoubleEntryLedger(), TccTransactionCoordinator(),
                                   idempotency_ttl_seconds=60.0, clock=clock)
    service.create_account("A", "USD", Decimal('1000'))
    service.create_account("B", "USD", Decimal('500'))
    status1 = service.transfer("A", "B", Decimal('100'), "USD", "tx-ttl")
    clock.advance(30)
    status2 = service.transfer("A", "B", Decimal('100'), "USD", "tx-ttl")
    assert status1.name == 'SUCCESS' and status2.name == 'SUCCESS'
    # Within the TTL the duplicate is rejected: money moved exactly once.
    assert service.get_account("A").balance == Decimal('900')


def test_idempotency_key_expires_after_ttl():
    clock = FakeClock()
    service = DigitalWalletService(DoubleEntryLedger(), TccTransactionCoordinator(),
                                   idempotency_ttl_seconds=60.0, clock=clock)
    service.create_account("A", "USD", Decimal('1000'))
    service.create_account("B", "USD", Decimal('500'))
    status1 = service.transfer("A", "B", Decimal('100'), "USD", "tx-ttl2")
    clock.advance(61)
    status2 = service.transfer("A", "B", Decimal('100'), "USD", "tx-ttl2")
    assert status1.name == 'SUCCESS' and status2.name == 'SUCCESS'
    # After expiry the key can be reused: a genuine retry executes again.
    assert service.get_account("A").balance == Decimal('800')
    assert service.get_account("B").balance == Decimal('700')
    assert "tx-ttl2" in service.idempotency_store


def test_expired_entries_purged_from_store():
    clock = FakeClock()
    service = DigitalWalletService(DoubleEntryLedger(), TccTransactionCoordinator(),
                                   idempotency_ttl_seconds=60.0, clock=clock)
    service.create_account("A", "USD", Decimal('1000'))
    service.create_account("B", "USD", Decimal('500'))
    service.transfer("A", "B", Decimal('50'), "USD", "tx-a")
    assert len(service.idempotency_store) == 1
    clock.advance(120)
    service.transfer("A", "B", Decimal('50'), "USD", "tx-b")  # triggers purge
    assert "tx-a" not in service.idempotency_store
    assert "tx-b" in service.idempotency_store


def test_default_store_has_no_expiry(wallet):
    # v1 parity: without a TTL the store rejects duplicates indefinitely.
    wallet.transfer("A", "B", Decimal('100'), "USD", "tx-no-ttl")
    status = wallet.transfer("A", "B", Decimal('100'), "USD", "tx-no-ttl")
    assert status.name == 'SUCCESS'
    assert wallet.get_account("A").balance == Decimal('900')
