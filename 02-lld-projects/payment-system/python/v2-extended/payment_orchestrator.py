"""PaymentOrchestrator for payment-system (v2-extended)."""
import threading
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass

from gateway_router_strategy import GatewayRouterStrategy
from idempotency_service import IdempotencyService

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

class PaymentOrchestrator:
    def __init__(self) -> None:
        self.id = "PaymentOrchestrator"
        self.gateway = GatewayRouterStrategy()
        self.idempotency = IdempotencyService()
        self.transactions: Dict[str, Transaction] = {}
        self._lock = threading.RLock()
        self.tx_counter = 0

    def process_payment(self, req: PaymentRequest) -> Dict[str, Any]:
        payload_hash = f"{req.amount}-{req.currency}-{req.token}"
        
        # 1. Idempotency Check
        cached_response = self.idempotency.check_or_acquire(req.idempotency_key, payload_hash)
        if cached_response is not None:
            return cached_response
            
        # 2. Database Initialization
        with self._lock:
            self.tx_counter += 1
            tx_id = f"tx_{self.tx_counter}"
            tx = Transaction(
                id=tx_id,
                idempotency_key=req.idempotency_key,
                amount=req.amount,
                state=TransactionState.INITIATED
            )
            self.transactions[tx_id] = tx
            
        # 3. Gateway Invocation
        with self._lock:
            if self.transactions[tx_id].state == TransactionState.INITIATED:
                self.transactions[tx_id].state = TransactionState.GATEWAY_PENDING
                
        response = None
        try:
            gw_resp = self.gateway.charge(req.amount, req.token)
            with self._lock:
                current_state = self.transactions[tx_id].state
                if current_state in (TransactionState.COMPLETED, TransactionState.DECLINED, TransactionState.FAILED):
                    response = {"status": current_state.name, "transaction_id": tx_id}
                elif gw_resp["status"] == "SUCCESS":
                    self.transactions[tx_id].state = TransactionState.COMPLETED
                    self.transactions[tx_id].gateway_reference_id = gw_resp.get("reference_id")
                    response = {"status": "SUCCESS", "transaction_id": tx_id}
                else:
                    self.transactions[tx_id].state = TransactionState.DECLINED
                    response = {"status": "DECLINED", "transaction_id": tx_id}
        except TimeoutError:
            with self._lock:
                current_state = self.transactions[tx_id].state
                if current_state in (TransactionState.COMPLETED, TransactionState.DECLINED, TransactionState.FAILED):
                    response = {"status": current_state.name, "transaction_id": tx_id}
                else:
                    # State remains GATEWAY_PENDING
                    response = {"status": "PENDING", "transaction_id": tx_id}
        except Exception:
            with self._lock:
                current_state = self.transactions[tx_id].state
                if current_state in (TransactionState.COMPLETED, TransactionState.DECLINED, TransactionState.FAILED):
                    response = {"status": current_state.name, "transaction_id": tx_id}
                else:
                    self.transactions[tx_id].state = TransactionState.FAILED
                    response = {"status": "FAILED", "transaction_id": tx_id}

        self.idempotency.save_response(req.idempotency_key, response)
        return response

    def reconcile_transaction(self, tx_id: str, new_state_str: str) -> None:
        """Called by webhook handler or background jobs."""
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
        return f"PaymentOrchestrator:{self.id}"
