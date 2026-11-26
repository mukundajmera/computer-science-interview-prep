import hashlib
import uuid
import time
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List, Any

class PaymentState:
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    PROCESSING_UNKNOWN = "PROCESSING_UNKNOWN"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED"
    FAILED = "FAILED"
    VOIDED = "VOIDED"

class TransactionStatus:
    PENDING = "PENDING"
    IN_FLIGHT = "IN_FLIGHT"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

class TransactionType:
    AUTHORIZE = "AUTHORIZE"
    CAPTURE = "CAPTURE"
    REFUND = "REFUND"
    VOID = "VOID"
    TRANSFER = "TRANSFER"

class DistributedPaymentService:
    def __init__(self, region_id: str):
        self.region_id = region_id
        self.intents: Dict[str, Dict[str, Any]] = {}
        self.idempotency_records: Dict[str, Dict[str, Any]] = {}
        self.transactions: List[Dict[str, Any]] = []
        self.outbox: List[Dict[str, Any]] = []

        self.is_partition_tolerant_degraded = False

        # Simulating distributed lock manager
        self._distributed_locks: Dict[str, Lock] = {}
        self._lock_manager_mutex = Lock()

    def set_degraded_mode(self, degraded: bool):
        self.is_partition_tolerant_degraded = degraded

    def _hash_payload(self, payload: str) -> str:
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def _acquire_lock(self, key: str):
        with self._lock_manager_mutex:
            if key not in self._distributed_locks:
                self._distributed_locks[key] = Lock()
            lock = self._distributed_locks[key]
        lock.acquire()

    def _release_lock(self, key: str):
        with self._lock_manager_mutex:
            if key in self._distributed_locks:
                self._distributed_locks[key].release()

    def create_or_confirm_intent(self, idempotency_key: str, merchant_id: str, customer_id: str, amount_minor: int, currency: str) -> Any:
        payload = f"{merchant_id}{customer_id}{amount_minor}{currency}"
        payload_hash = self._hash_payload(payload)
        lock_key = f"idem_{idempotency_key}"

        self._acquire_lock(lock_key)
        try:
            now = datetime.now(timezone.utc).timestamp()
            record = self.idempotency_records.get(idempotency_key)

            if record:
                if record["payload_hash"] != payload_hash:
                    raise ValueError("duplicate_idempotency_key")

                if record["state"] == "SUCCEEDED":
                    return record["response"]

                if record["state"] == "IN_PROGRESS" and record["lease_expires_at"] > now:
                    return "202_ACCEPTED"
            else:
                record = {
                    "idempotency_key": idempotency_key,
                    "payload_hash": payload_hash
                }

            record["state"] = "IN_PROGRESS"
            record["lock_owner"] = f"{self.region_id}_{uuid.uuid4()}"
            record["lease_expires_at"] = now + 30
            self.idempotency_records[idempotency_key] = record

            intent_id = f"pi_{uuid.uuid4()}"
            intent = {
                "id": intent_id,
                "merchant_id": merchant_id,
                "customer_id": customer_id,
                "amount_minor": amount_minor,
                "currency": currency,
                "state": PaymentState.CREATED,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "captured_amount": 0,
                "refunded_amount": 0
            }
            self.intents[intent_id] = intent

            # Confirm
            intent["state"] = PaymentState.PROCESSING

            txn_id = f"txn_{uuid.uuid4()}"
            txn = {
                "transaction_id": txn_id,
                "intent_id": intent_id,
                "type": TransactionType.AUTHORIZE,
                "amount": amount_minor,
                "status": TransactionStatus.IN_FLIGHT,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self.transactions.append(txn)

            if self.is_partition_tolerant_degraded:
                intent["state"] = PaymentState.PROCESSING
                txn["status"] = TransactionStatus.UNKNOWN

                self.outbox.append({
                    "id": str(uuid.uuid4()),
                    "intent_id": intent_id,
                    "event_type": "ASYNC_AUTH_POLL",
                    "status": "PENDING",
                    "created_at": datetime.now(timezone.utc).isoformat()
                })

                record["state"] = "SUCCEEDED"
                record["response"] = intent
                return intent
            else:
                intent["state"] = PaymentState.AUTHORIZED
                txn["status"] = TransactionStatus.SUCCESS

                record["state"] = "SUCCEEDED"
                record["response"] = intent
                return intent

        finally:
            self._release_lock(lock_key)

    def capture(self, intent_id: str) -> Dict[str, Any]:
        self._acquire_lock(f"intent_{intent_id}")
        try:
            intent = self.intents.get(intent_id)
            if not intent:
                raise ValueError("Intent not found")
            if intent["state"] != PaymentState.AUTHORIZED:
                raise ValueError("invalid_state_transition")

            intent["state"] = PaymentState.CAPTURED
            intent["captured_amount"] = intent["amount_minor"]

            txn_id = f"txn_{uuid.uuid4()}"
            txn = {
                "transaction_id": txn_id,
                "intent_id": intent_id,
                "type": TransactionType.CAPTURE,
                "amount": intent["amount_minor"],
                "status": TransactionStatus.SUCCESS,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            self.transactions.append(txn)
            return txn
        finally:
            self._release_lock(f"intent_{intent_id}")

    def handle_provider_webhook(self, intent_id: str, status: str):
        self._acquire_lock(f"intent_{intent_id}")
        try:
            intent = self.intents.get(intent_id)
            if intent and intent["state"] == PaymentState.PROCESSING:
                if status == "SUCCESS":
                    intent["state"] = PaymentState.AUTHORIZED
                    self._update_transaction_status(intent_id, TransactionType.AUTHORIZE, TransactionStatus.SUCCESS)
                elif status == "FAILED":
                    intent["state"] = PaymentState.FAILED
                    self._update_transaction_status(intent_id, TransactionType.AUTHORIZE, TransactionStatus.FAILED)
        finally:
            self._release_lock(f"intent_{intent_id}")

    def _update_transaction_status(self, intent_id: str, txn_type: str, status: str):
        for txn in self.transactions:
            if txn["intent_id"] == intent_id and txn["type"] == txn_type:
                txn["status"] = status
                break

    def execute_transfer_saga(self, from_account: str, to_account: str, amount: int) -> Dict[str, Any]:
        saga = {
            "saga_id": str(uuid.uuid4()),
            "steps_completed": [],
            "compensated": False
        }

        debit_success = False
        credit_success = False

        try:
            debit_success = self._simulate_service_call(from_account, -amount)
            if debit_success:
                saga["steps_completed"].append("DEBIT")
            else:
                raise RuntimeError("Debit failed")

            credit_success = self._simulate_service_call(to_account, amount)
            if credit_success:
                saga["steps_completed"].append("CREDIT")
            else:
                raise RuntimeError("Credit failed")

            return saga
        except Exception as e:
            if debit_success and not credit_success:
                self._simulate_service_call(from_account, amount) # refund
                saga["compensated"] = True
            raise RuntimeError(f"Saga aborted and compensated: {str(e)}")

    def _simulate_service_call(self, account: str, amount: int) -> bool:
        return "fail" not in account

    def get_intent(self, intent_id: str) -> Dict[str, Any]:
        return self.intents.get(intent_id)
