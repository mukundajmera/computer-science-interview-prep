"""CircuitBreakerGatewayClient for payment-system (v3-optimized)."""
from typing import Dict, Any


class CircuitBreakerGatewayClient:
    def __init__(self) -> None:
        self.id = "CircuitBreakerGatewayClient"

    def charge(self, amount: int, token: str) -> Dict[str, Any]:
        """
        Simulates an external gateway with circuit breaker capabilities.
        amount=1000 => SUCCESS
        amount=2000 => DECLINED
        amount=3000 => TIMEOUT (simulate ambiguous timeout)
        """
        if amount == 2000:
            return {"status": "DECLINED"}
        if amount == 3000:
            raise TimeoutError("Ambiguous gateway timeout")
        if amount == 4000:
            raise Exception("Gateway crash")
            
        return {"status": "SUCCESS", "reference_id": f"ref_{token}"}

    def describe(self) -> str:
        return f"CircuitBreakerGatewayClient:{self.id}"
