import threading
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional, Tuple

from double_entry_ledger import DoubleEntryLedger, LedgerEntry, EntryType

class Phase(Enum):
    TRY = "TRY"
    CONFIRM = "CONFIRM"
    CANCEL = "CANCEL"

class Status(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class TransactionState:
    def __init__(self, transaction_id: str, from_account: str, to_account: str, amount: Decimal):
        self.transaction_id = transaction_id
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.phase = Phase.TRY
        self.status = Status.PENDING
        self.out_of_order_flag = False
        self.updated_at = datetime.now(timezone.utc)

class TccTransactionCoordinator:
    def __init__(self):
        self._active_transactions: Dict[str, TransactionState] = {}
        self._lock = threading.Lock()

    def initiate_try(self, transaction_id: str, from_account: str, to_account: str, amount: Decimal) -> TransactionState:
        with self._lock:
            state = TransactionState(transaction_id, from_account, to_account, amount)
            self._active_transactions[transaction_id] = state
            return state

    def confirm(self, transaction_id: str) -> TransactionState:
        with self._lock:
            state = self._active_transactions.get(transaction_id)
            if not state:
                raise ValueError(f"Transaction not found: {transaction_id}")
            if state.status == Status.FAILED and state.phase == Phase.CANCEL:
                raise ValueError("Cannot confirm a cancelled transaction")
            if state.phase == Phase.CANCEL and state.out_of_order_flag:
                raise ValueError("Transaction was already marked for cancellation")
            
            state.phase = Phase.CONFIRM
            state.status = Status.SUCCESS
            state.updated_at = datetime.now(timezone.utc)
            return state

    def cancel(self, transaction_id: str) -> TransactionState:
        with self._lock:
            state = self._active_transactions.get(transaction_id)
            if not state:
                # Out of order: Cancel before Try
                state = TransactionState(transaction_id, "unknown", "unknown", Decimal('0'))
                state.out_of_order_flag = True
                state.phase = Phase.CANCEL
                state.status = Status.FAILED
                self._active_transactions[transaction_id] = state
                return state
            
            if state.phase == Phase.CONFIRM:
                raise ValueError("Cannot cancel an already confirmed transaction")
            
            state.phase = Phase.CANCEL
            state.status = Status.FAILED
            state.updated_at = datetime.now(timezone.utc)
            return state

    def get_state(self, transaction_id: str) -> Optional[TransactionState]:
        with self._lock:
            return self._active_transactions.get(transaction_id)

class Account:
    def __init__(self, account_id: str, currency: str, balance: Decimal):
        self.account_id = account_id
        self.currency = currency
        self.balance = balance
        self.held_balance = Decimal('0')

class DigitalWalletService:
    def __init__(self, ledger: DoubleEntryLedger, coordinator: TccTransactionCoordinator):
        self.ledger = ledger
        self.coordinator = coordinator
        self.accounts: Dict[str, Account] = {}
        self.idempotency_store: Dict[str, str] = {}
        self._lock = threading.RLock()

    def create_account(self, account_id: str, currency: str, initial_balance: Decimal):
        with self._lock:
            self.accounts[account_id] = Account(account_id, currency, initial_balance)
            if initial_balance > Decimal('0'):
                transaction_id = str(uuid.uuid4())
                credit = LedgerEntry(transaction_id, account_id, EntryType.CREDIT, initial_balance, currency)
                debit = LedgerEntry(transaction_id, "SYSTEM", EntryType.DEBIT, initial_balance, currency)
                self.ledger.commit_transaction([credit, debit])

    def get_account(self, account_id: str) -> Optional[Account]:
        with self._lock:
            return self.accounts.get(account_id)

    def transfer(self, from_account: str, to_account: str, amount: Decimal, currency: str, idempotency_key: str) -> Status:
        with self._lock:
            if idempotency_key in self.idempotency_store:
                tx_id = self.idempotency_store[idempotency_key]
                state = self.coordinator.get_state(tx_id)
                return state.status if state else Status.PENDING

            transaction_id = str(uuid.uuid4())
            self.idempotency_store[idempotency_key] = transaction_id

            src = self.accounts.get(from_account)
            dest = self.accounts.get(to_account)

            if src is None or dest is None:
                self.coordinator.initiate_try(transaction_id, from_account, to_account, amount)
                self.coordinator.cancel(transaction_id)
                return Status.FAILED

            if src.balance < amount:
                self.coordinator.initiate_try(transaction_id, from_account, to_account, amount)
                self.coordinator.cancel(transaction_id)
                return Status.FAILED

            # TRY
            self.coordinator.initiate_try(transaction_id, from_account, to_account, amount)
            src.balance -= amount
            src.held_balance += amount

            # Process
            try:
                state = self.coordinator.get_state(transaction_id)
                if state and state.out_of_order_flag:
                    raise ValueError("Out of order cancel flag detected")

                # CONFIRM
                self.coordinator.confirm(transaction_id)
                src.held_balance -= amount
                dest.balance += amount

                debit = LedgerEntry(transaction_id, from_account, EntryType.DEBIT, amount, currency)
                credit = LedgerEntry(transaction_id, to_account, EntryType.CREDIT, amount, currency)
                self.ledger.commit_transaction([debit, credit])

                return Status.SUCCESS
            except Exception:
                # CANCEL
                self.coordinator.cancel(transaction_id)
                src.held_balance -= amount
                src.balance += amount
                return Status.FAILED

    def simulate_out_of_order_cancel(self, idempotency_key: str):
        with self._lock:
            tx_id = self.idempotency_store.get(idempotency_key)
            if not tx_id:
                tx_id = str(uuid.uuid4())
                self.idempotency_store[idempotency_key] = tx_id
            self.coordinator.cancel(tx_id)

    def replay_event_sourcing_history(self):
        with self._lock:
            for acc in self.accounts.values():
                acc.balance = Decimal('0')
                acc.held_balance = Decimal('0')

            entries = self.ledger.get_journal()
            for entry in entries:
                if entry.account_id == "SYSTEM":
                    continue
                acc = self.accounts.get(entry.account_id)
                if acc:
                    if entry.entry_type == EntryType.CREDIT:
                        acc.balance += entry.amount
                    elif entry.entry_type == EntryType.DEBIT:
                        acc.balance -= entry.amount
