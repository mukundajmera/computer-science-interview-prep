"""
Expense class for Splitwise - v1 Basic
"""
from typing import List, TYPE_CHECKING
from split import Split, SplitType

if TYPE_CHECKING:
    from user import User


class Expense:
    """Represents an expense in the Splitwise system."""
    
    def __init__(
        self,
        expense_id: str,
        amount: float,
        description: str,
        paid_by: "User",
        splits: List[Split],
        split_type: SplitType
    ):
        """
        Initialize an expense.
        
        Args:
            expense_id: Unique identifier for the expense
            amount: Total amount of the expense
            description: Description of the expense
            paid_by: User who paid for the expense
            splits: List of splits for participants
            split_type: Type of split (equal, exact, percentage)
        """
        self._expense_id = expense_id
        self._amount = amount
        self._description = description
        self._paid_by = paid_by
        self._splits = splits
        self._split_type = split_type
    
    @property
    def expense_id(self) -> str:
        """Get expense ID."""
        return self._expense_id
    
    @property
    def amount(self) -> float:
        """Get total amount."""
        return self._amount
    
    @property
    def description(self) -> str:
        """Get description."""
        return self._description
    
    @property
    def paid_by(self) -> "User":
        """Get user who paid."""
        return self._paid_by
    
    @property
    def splits(self) -> List[Split]:
        """Get list of splits."""
        return self._splits
    
    @property
    def split_type(self) -> SplitType:
        """Get split type."""
        return self._split_type
    
    def __repr__(self) -> str:
        return f"Expense(id={self._expense_id}, amount={self._amount}, type={self._split_type.value})"
