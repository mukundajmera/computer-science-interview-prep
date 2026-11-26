"""
Enums for ATM System.
"""
from enum import Enum


class AccountType(Enum):
    """Types of bank accounts."""
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"


class TransactionType(Enum):
    """Types of ATM transactions."""
    BALANCE_INQUIRY = "BALANCE_INQUIRY"
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"


class TransactionStatus(Enum):
    """Status of a transaction."""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
