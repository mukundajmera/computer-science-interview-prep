"""ReconciliationService for payment-system (v3-optimized)."""


class ReconciliationService:
    def __init__(self) -> None:
        self.id = "ReconciliationService"
        
    def resolve_timeout(self, payment_service, transaction_id: str, final_status_str: str) -> None:
        """
        Reconciles a timed-out transaction.
        """
        payment_service.handle_webhook(transaction_id, final_status_str)

    def describe(self) -> str:
        return f"ReconciliationService:{self.id}"
