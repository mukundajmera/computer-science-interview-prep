"""WebhookHandler for payment-system (v2-extended)."""
from typing import Any

class WebhookHandler:
    def __init__(self, orchestrator: Any) -> None:
        self.id = "WebhookHandler"
        self.orchestrator = orchestrator

    def handle_webhook(self, transaction_id: str, new_state: str) -> None:
        """
        Handle duplicate or out-of-order webhooks safely.
        """
        self.orchestrator.reconcile_transaction(transaction_id, new_state)

    def describe(self) -> str:
        return f"WebhookHandler:{self.id}"
