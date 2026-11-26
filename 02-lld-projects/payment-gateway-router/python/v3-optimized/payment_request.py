from dataclasses import dataclass
from typing import Optional

@dataclass
class PaymentRequest:
    id: str
    idempotency_key: Optional[str]
    amount: float
    currency: str
    user_id: str
