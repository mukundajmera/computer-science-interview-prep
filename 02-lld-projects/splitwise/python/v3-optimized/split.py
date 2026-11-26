"""
Split classes for Splitwise - v1 Basic
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from user import User


class SplitType(Enum):
    """Types of expense splits."""
    EQUAL = "EQUAL"
    EXACT = "EXACT"
    PERCENTAGE = "PERCENTAGE"


class Split(ABC):
    """Abstract base class for expense splits."""
    
    def __init__(self, user: "User"):
        """
        Initialize a split.
        
        Args:
            user: The user this split belongs to
        """
        self._user = user
        self._amount = 0.0
    
    @property
    def user(self) -> "User":
        """Get the user."""
        return self._user
    
    @property
    def amount(self) -> float:
        """Get the split amount."""
        return self._amount
    
    @amount.setter
    def amount(self, value: float):
        """Set the split amount."""
        self._amount = value
    
    @abstractmethod
    def get_split_type(self) -> SplitType:
        """Get the type of split."""
        pass


class EqualSplit(Split):
    """Equal split - amount divided equally among participants."""
    
    def get_split_type(self) -> SplitType:
        return SplitType.EQUAL


class ExactSplit(Split):
    """Exact split - specific amount for each participant."""
    
    def __init__(self, user: "User", amount: float):
        super().__init__(user)
        self._amount = amount
    
    def get_split_type(self) -> SplitType:
        return SplitType.EXACT


class PercentageSplit(Split):
    """Percentage split - percentage of total for each participant."""
    
    def __init__(self, user: "User", percentage: float):
        super().__init__(user)
        self._percentage = percentage
    
    @property
    def percentage(self) -> float:
        """Get the percentage."""
        return self._percentage
    
    def get_split_type(self) -> SplitType:
        return SplitType.PERCENTAGE
