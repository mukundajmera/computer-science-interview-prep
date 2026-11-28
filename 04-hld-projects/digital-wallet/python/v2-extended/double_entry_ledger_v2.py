import threading
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from enum import Enum
from typing import List


class EntryType(Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class LedgerEntry:
    def __init__(self, transaction_id: str, account_id: str, entry_type: EntryType, amount: Decimal, currency: str):
        self.entry_id = str(uuid.uuid4())
        self.transaction_id = transaction_id
        self.account_id = account_id
        self.entry_type = entry_type
        self.amount = amount
        self.currency = currency
        self.created_at = datetime.now(timezone.utc)


class DoubleEntryLedger:
    """Unchanged from v1: the double-entry invariant is already correct."""

    def __init__(self):
        self._journal: List[LedgerEntry] = []
        self._lock = threading.Lock()

    def commit_transaction(self, entries: List[LedgerEntry]):
        with self._lock:
            total_debit = Decimal('0')
            total_credit = Decimal('0')

            for entry in entries:
                if entry.entry_type == EntryType.DEBIT:
                    total_debit += entry.amount
                elif entry.entry_type == EntryType.CREDIT:
                    total_credit += entry.amount

            if total_debit != total_credit:
                raise ValueError(f"Double-entry invariant violated: Debits ({total_debit}) do not equal Credits ({total_credit})")

            self._journal.extend(entries)

    def get_journal(self) -> List[LedgerEntry]:
        with self._lock:
            return list(self._journal)
