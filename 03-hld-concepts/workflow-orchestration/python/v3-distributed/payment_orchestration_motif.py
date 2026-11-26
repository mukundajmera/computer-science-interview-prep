class PaymentOrchestrationMotif:
    def should_compensate(self, status: str) -> bool:
        return status.upper() == "FAILED"
