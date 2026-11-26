from enum import Enum, auto

class OrderStatus(Enum):
    PLACED = auto()
    PREPARING = auto()
    READY_FOR_PICKUP = auto()
    OUT_FOR_DELIVERY = auto()
    DELIVERED = auto()
    CANCELLED = auto()
