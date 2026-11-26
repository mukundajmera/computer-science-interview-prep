"""v3-advanced: Resilient Financial Transaction Template with Compensation Hooks.

Defines the transactional algorithm invariant (Pre-auth -> Fraud hook -> Debit -> Audit -> Compensate hook),
protecting accounts against half-completed operations.
"""
from abc import ABC, abstractmethod
from typing import List


class TransactionResult:
    def __init__(self, success: bool, txn_id: str, message: str, audit_logs: List[str]) -> None:
        self.success: bool = success
        self.txn_id: str = txn_id
        self.message: str = message
        self.audit_logs: List[str] = list(audit_logs)


class PaymentProcessorTemplate(ABC):
    def __init__(self) -> None:
        self.logs: List[str] = []

    def process_payment(self, txn_id: str, amount: float, currency: str) -> TransactionResult:
        """The Template Method defining the financial execution flow."""
        self.logs.clear()
        self.logs.append(f"Txn started: {txn_id} amount: {amount} {currency}")

        if amount <= 0:
            self.logs.append(f"Amount validation failed: {amount}")
            return TransactionResult(False, txn_id, "Invalid amount", self.logs)

        if not self.pre_authorize(txn_id, amount):
            self.logs.append("Pre-authorization declined")
            return TransactionResult(False, txn_id, "Pre-auth failed", self.logs)

        if self.requires_fraud_check() and not self.pass_fraud_check(txn_id, amount):
            self.logs.append("Fraud check triggered alert; compensating")
            self.compensate(txn_id, "Flagged by fraud detector")
            return TransactionResult(False, txn_id, "Fraud check failed", self.logs)

        charged = self.execute_debit(txn_id, amount)
        if not charged:
            self.logs.append("Debit failed; rolling back authorization")
            self.compensate(txn_id, "Debit failure")
            return TransactionResult(False, txn_id, "Payment debit declined", self.logs)

        self.record_audit_success(txn_id, amount)
        self.logs.append("Transaction committed successfully")
        return TransactionResult(True, txn_id, "Success", self.logs)

    @abstractmethod
    def pre_authorize(self, txn_id: str, amount: float) -> bool:
        pass

    @abstractmethod
    def execute_debit(self, txn_id: str, amount: float) -> bool:
        pass

    # Hooks
    def requires_fraud_check(self) -> bool:
        return True

    def pass_fraud_check(self, txn_id: str, amount: float) -> bool:
        return amount < 10000.0

    def compensate(self, txn_id: str, reason: str) -> None:
        self.logs.append(f"Compensation executed for {txn_id}: {reason}")

    def record_audit_success(self, txn_id: str, amount: float) -> None:
        self.logs.append(f"Audit record stored for {txn_id}")


class CreditCardProcessor(PaymentProcessorTemplate):
    def pre_authorize(self, txn_id: str, amount: float) -> bool:
        self.logs.append("Visa/Mastercard pre-auth approved")
        return True

    def execute_debit(self, txn_id: str, amount: float) -> bool:
        self.logs.append("Card charged successfully")
        return True


class HighRiskCryptoProcessor(PaymentProcessorTemplate):
    def __init__(self, simulate_network_drop: bool = False) -> None:
        super().__init__()
        self._simulate_network_drop = simulate_network_drop

    def pre_authorize(self, txn_id: str, amount: float) -> bool:
        self.logs.append("Wallet signature validated")
        return True

    def execute_debit(self, txn_id: str, amount: float) -> bool:
        if self._simulate_network_drop:
            self.logs.append("Blockchain node timeout")
            return False
        self.logs.append("Gas fee paid and transaction mined")
        return True

    def requires_fraud_check(self) -> bool:
        return False
