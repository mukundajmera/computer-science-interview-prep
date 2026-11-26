"""PaymentService for payment-system (v3-optimized)."""
import threading
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass

from circuit_breaker_gateway_client import CircuitBreakerGatewayClient

class TransactionState(Enum):
    INITIATED = "INITIATED"
    GATEWAY_PENDING = "GATEWAY_PENDING"
    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"
    FAILED = "FAILED"

@dataclass
class PaymentRequest:
    idempotency_key: str
    amount: int
    currency: str
    token: str

@dataclass
class Transaction:
    id: str
    idempotency_key: str
    amount: int
    state: TransactionState
    gateway_reference_id: Optional[str] = None

class PaymentService:
    def __init__(self) -> None:
        self.id = "PaymentService"
        self.gateway = CircuitBreakerGatewayClient()
        
        self.idempotency_store: Dict[str, Dict[str, Any]] = {}
        self.transactions: Dict[str, Transaction] = {}
        self._lock = threading.Lock()
        self.tx_counter = 0
        
    def process_payment(self, req: PaymentRequest) -> Dict[str, Any]:
        payload_hash = f"{req.amount}-{req.currency}-{req.token}"
        
        with self._lock:
            if req.idempotency_key in self.idempotency_store:
                entry = self.idempotency_store[req.idempotency_key]
                if entry['payload_hash'] != payload_hash:
                    raise ValueError("Repeated idempotency key with changed payload")
                if entry['response'] is None:
                    return {"status": "IN_PROGRESS", "message": "Request currently processing"}
                return entry['response']
            else:
                self.idempotency_store[req.idempotency_key] = {
                    'payload_hash': payload_hash,
                    'response': None
                }
            
            # 2. Database Initialization
            self.tx_counter += 1
            tx_id = f"tx_{self.tx_counter}"
            tx = Transaction(
                id=tx_id,
                idempotency_key=req.idempotency_key,
                amount=req.amount,
                state=TransactionState.INITIATED
            )
            self.transactions[tx_id] = tx
            
            # 3. State transition before Gateway Invocation
            self.transactions[tx_id].state = TransactionState.GATEWAY_PENDING
                
        response = None
        try:
            gw_resp = self.gateway.charge(req.amount, req.token)
            with self._lock:
                # Check if state is already terminal due to out-of-order webhooks
                current_state = self.transactions[tx_id].state
                if current_state not in (TransactionState.COMPLETED, TransactionState.DECLINED, TransactionState.FAILED):
                    if gw_resp["status"] == "SUCCESS":
                        self.transactions[tx_id].state = TransactionState.COMPLETED
                        self.transactions[tx_id].gateway_reference_id = gw_resp.get("reference_id")
                        response = {"status": "SUCCESS", "transaction_id": tx_id}
                    else:
                        self.transactions[tx_id].state = TransactionState.DECLINED
                        response = {"status": "DECLINED", "transaction_id": tx_id}
                else:
                    response = {"status": current_state.value, "transaction_id": tx_id}
        except TimeoutError:
            # State remains GATEWAY_PENDING
            response = {"status": "PENDING", "transaction_id": tx_id}
        except Exception:
            with self._lock:
                current_state = self.transactions[tx_id].state
                if current_state not in (TransactionState.COMPLETED, TransactionState.DECLINED, TransactionState.FAILED):
                    self.transactions[tx_id].state = TransactionState.FAILED
            response = {"status": "FAILED", "transaction_id": tx_id}

        with self._lock:
            if req.idempotency_key in self.idempotency_store:
                self.idempotency_store[req.idempotency_key]['response'] = response

        return response

    def handle_webhook(self, tx_id: str, new_state_str: str) -> None:
        """Called by webhook handler or background jobs to safely update out-of-order webhooks."""
        with self._lock:
            if tx_id not in self.transactions:
                return
            
            current_state = self.transactions[tx_id].state
            # Ignore if already in terminal state
            if current_state in (TransactionState.COMPLETED, TransactionState.DECLINED, TransactionState.FAILED):
                return
                
            try:
                new_state = TransactionState(new_state_str)
                self.transactions[tx_id].state = new_state
            except ValueError:
                pass

    def describe(self) -> str:
        return f"PaymentService:{self.id}"
