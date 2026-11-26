from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

class PaymentStatus(Enum):
    SUCCESS = auto()
    FAILED = auto()
    TIMEOUT = auto()
    CONFLICT = auto()

@dataclass
class PaymentResponse:
    transaction_id: Optional[str]
    status: PaymentStatus
    message: str
    gateway_name: Optional[str]
