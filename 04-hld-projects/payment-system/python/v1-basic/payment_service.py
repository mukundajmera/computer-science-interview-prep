from enum import Enum
from typing import Dict, List, Any
import uuid
import datetime
import hashlib
from threading import Lock

class PaymentState(Enum):
    CREATED = 1
    PROCESSING = 2
    AUTHORIZED = 3
    CAPTURED = 4
    REFUND_PENDING = 5
    REFUNDED = 6
    PARTIALLY_REFUNDED = 7
    FAILED = 8
    VOIDED = 9

class TransactionType(Enum):
    AUTHORIZE = 1
    CAPTURE = 2
    REFUND = 3
    VOID = 4

class PaymentIntent:
    def __init__(self, id: str, merchant_id: str, customer_id: str, amount_minor: int, currency: str):
        self.id = id
        self.merchant_id = merchant_id
        self.customer_id = customer_id
        self.amount_minor = amount_minor
        self.currency = currency
        self.state = PaymentState.CREATED
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
        self.captured_amount = 0
        self.refunded_amount = 0

class IdempotencyRecord:
    def __init__(self, idempotency_key: str, payload_hash: str, response: Any):
        self.idempotency_key = idempotency_key
        self.payload_hash = payload_hash
        self.response = response

class PaymentTransaction:
    def __init__(self, transaction_id: str, intent_id: str, transaction_type: TransactionType, amount: int):
        self.transaction_id = transaction_id
        self.intent_id = intent_id
        self.type = transaction_type
        self.amount = amount
        self.created_at = datetime.datetime.now(datetime.timezone.utc)

class LedgerEntry:
    def __init__(self, id: str, transaction_id: str, account_id: str, amount: int):
        self.id = id
        self.transaction_id = transaction_id
        self.account_id = account_id
        self.amount = amount  # positive for credit, negative for debit
        self.created_at = datetime.datetime.now(datetime.timezone.utc)

class PaymentService:
    def __init__(self):
        self.intents: Dict[str, PaymentIntent] = {}
        self.idempotency_records: Dict[str, IdempotencyRecord] = {}
        self.transactions: List[PaymentTransaction] = []
        self.ledger: List[LedgerEntry] = []
        self.lock = Lock()

    def _hash_payload(self, payload: str) -> str:
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def _record_ledger(self, transaction_id: str, from_account: str, to_account: str, amount: int):
        debit = LedgerEntry(
            id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            account_id=from_account,
            amount=-amount
        )
        credit = LedgerEntry(
            id=str(uuid.uuid4()),
            transaction_id=transaction_id,
            account_id=to_account,
            amount=amount
        )
        self.ledger.append(debit)
        self.ledger.append(credit)

    def create_payment_intent(self, idempotency_key: str, merchant_id: str, customer_id: str, amount_minor: int, currency: str) -> PaymentIntent:
        payload = f"{merchant_id}{customer_id}{amount_minor}{currency}"
        payload_hash = self._hash_payload(payload)

        with self.lock:
            if idempotency_key in self.idempotency_records:
                record = self.idempotency_records[idempotency_key]
                if record.payload_hash != payload_hash:
                    raise ValueError("duplicate_idempotency_key")
                return record.response

            intent_id = f"pi_{uuid.uuid4()}"
            intent = PaymentIntent(
                id=intent_id,
                merchant_id=merchant_id,
                customer_id=customer_id,
                amount_minor=amount_minor,
                currency=currency
            )

            self.intents[intent_id] = intent

            record = IdempotencyRecord(
                idempotency_key=idempotency_key,
                payload_hash=payload_hash,
                response=intent
            )
            self.idempotency_records[idempotency_key] = record

            return intent

    def authorize(self, intent_id: str) -> PaymentTransaction:
        with self.lock:
            intent = self.intents.get(intent_id)
            if not intent:
                raise KeyError("Intent not found")
            if intent.state != PaymentState.CREATED:
                raise ValueError("invalid_state_transition")

            intent.state = PaymentState.AUTHORIZED

            txn_id = f"txn_{uuid.uuid4()}"
            txn = PaymentTransaction(
                transaction_id=txn_id,
                intent_id=intent_id,
                transaction_type=TransactionType.AUTHORIZE,
                amount=intent.amount_minor
            )
            self.transactions.append(txn)

            return txn

    def capture(self, intent_id: str) -> PaymentTransaction:
        with self.lock:
            intent = self.intents.get(intent_id)
            if not intent:
                raise KeyError("Intent not found")
            if intent.state != PaymentState.AUTHORIZED:
                raise ValueError("invalid_state_transition")

            intent.state = PaymentState.CAPTURED
            intent.captured_amount = intent.amount_minor

            txn_id = f"txn_{uuid.uuid4()}"
            txn = PaymentTransaction(
                transaction_id=txn_id,
                intent_id=intent_id,
                transaction_type=TransactionType.CAPTURE,
                amount=intent.amount_minor
            )
            self.transactions.append(txn)

            self._record_ledger(txn.transaction_id, intent.customer_id, intent.merchant_id, intent.amount_minor)

            return txn

    def refund(self, intent_id: str, amount: int) -> PaymentTransaction:
        with self.lock:
            intent = self.intents.get(intent_id)
            if not intent:
                raise KeyError("Intent not found")
            if intent.state not in (PaymentState.CAPTURED, PaymentState.PARTIALLY_REFUNDED):
                raise ValueError("invalid_state_transition")
            if intent.refunded_amount + amount > intent.captured_amount:
                raise ValueError("Refund amount exceeds captured amount")

            intent.state = PaymentState.REFUND_PENDING
            # Simulating immediate success for basic v1
            intent.refunded_amount += amount
            if intent.refunded_amount == intent.captured_amount:
                intent.state = PaymentState.REFUNDED
            else:
                intent.state = PaymentState.PARTIALLY_REFUNDED

            txn_id = f"txn_{uuid.uuid4()}"
            txn = PaymentTransaction(
                transaction_id=txn_id,
                intent_id=intent_id,
                transaction_type=TransactionType.REFUND,
                amount=amount
            )
            self.transactions.append(txn)

            self._record_ledger(txn.transaction_id, intent.merchant_id, intent.customer_id, amount)

            return txn

    def void_payment(self, intent_id: str) -> PaymentTransaction:
        with self.lock:
            intent = self.intents.get(intent_id)
            if not intent:
                raise KeyError("Intent not found")
            if intent.state != PaymentState.AUTHORIZED:
                raise ValueError("invalid_state_transition")

            intent.state = PaymentState.VOIDED

            txn_id = f"txn_{uuid.uuid4()}"
            txn = PaymentTransaction(
                transaction_id=txn_id,
                intent_id=intent_id,
                transaction_type=TransactionType.VOID,
                amount=intent.amount_minor
            )
            self.transactions.append(txn)

            return txn

    def get_intent(self, intent_id: str) -> PaymentIntent:
        return self.intents.get(intent_id)

    def get_transactions(self, intent_id: str) -> List[PaymentTransaction]:
        return [txn for txn in self.transactions if txn.intent_id == intent_id]

    def get_ledger(self) -> List[LedgerEntry]:
        return list(self.ledger)
