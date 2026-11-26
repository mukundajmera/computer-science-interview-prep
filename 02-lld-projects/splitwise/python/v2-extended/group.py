"""
Group class for Splitwise - v2 Extended
"""
from typing import List, Dict, Set
from collections import defaultdict

# Import from v1 with adjusted paths for typing
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from user import User


class Group:
    """Represents a group of users for shared expenses."""
    
    def __init__(self, group_id: str, name: str, created_by: "User"):
        """
        Initialize a group.
        
        Args:
            group_id: Unique identifier for the group
            name: Name of the group
            created_by: User who created the group
        """
        self._group_id = group_id
        self._name = name
        self._created_by = created_by
        self._members: Dict[str, "User"] = {created_by.user_id: created_by}
        self._expense_ids: List[str] = []
    
    @property
    def group_id(self) -> str:
        """Get group ID."""
        return self._group_id
    
    @property
    def name(self) -> str:
        """Get group name."""
        return self._name
    
    @property
    def members(self) -> List["User"]:
        """Get list of members."""
        return list(self._members.values())
    
    @property
    def member_ids(self) -> Set[str]:
        """Get set of member IDs."""
        return set(self._members.keys())
    
    @property
    def expense_ids(self) -> List[str]:
        """Get list of expense IDs in this group."""
        return self._expense_ids.copy()
    
    def add_member(self, user: "User") -> bool:
        """Add a member to the group."""
        if user.user_id in self._members:
            return False
        self._members[user.user_id] = user
        return True
    
    def remove_member(self, user_id: str) -> bool:
        """Remove a member from the group."""
        if user_id == self._created_by.user_id:
            return False  # Cannot remove creator
        if user_id not in self._members:
            return False
        del self._members[user_id]
        return True
    
    def add_expense_id(self, expense_id: str) -> None:
        """Add an expense ID to the group."""
        self._expense_ids.append(expense_id)
    
    def is_member(self, user_id: str) -> bool:
        """Check if user is a member."""
        return user_id in self._members
    
    def __repr__(self) -> str:
        return f"Group(id={self._group_id}, name={self._name}, members={len(self._members)})"
