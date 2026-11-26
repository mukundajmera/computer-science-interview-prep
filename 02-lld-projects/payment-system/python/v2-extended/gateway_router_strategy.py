"""GatewayRouterStrategy for payment-system (v2-extended)."""
from typing import Dict, Any

class GatewayRouterStrategy:
    def __init__(self) -> None:
        self.id = "GatewayRouterStrategy"

    def charge(self, amount: int, token: str) -> Dict[str, Any]:
        """
        Simulates an external gateway.
        amount=1000 => SUCCESS
        amount=2000 => DECLINED
        amount=3000 => TIMEOUT (simulate ambiguous timeout)
        """
        if amount == 2000:
            return {"status": "DECLINED"}
        if amount == 3000:
            raise TimeoutError("Ambiguous gateway timeout")
            
        return {"status": "SUCCESS", "reference_id": f"ref_{token}"}

    def describe(self) -> str:
        return f"GatewayRouterStrategy:{self.id}"
