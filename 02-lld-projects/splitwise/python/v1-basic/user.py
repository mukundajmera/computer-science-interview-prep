"""
User class for Splitwise - v1 Basic
"""


class User:
    """Represents a user in the Splitwise system."""
    
    def __init__(self, user_id: str, name: str, email: str):
        """
        Initialize a user.
        
        Args:
            user_id: Unique identifier for the user
            name: Name of the user
            email: Email address of the user
        """
        self._user_id = user_id
        self._name = name
        self._email = email
    
    @property
    def user_id(self) -> str:
        """Get user ID."""
        return self._user_id
    
    @property
    def name(self) -> str:
        """Get user name."""
        return self._name
    
    @property
    def email(self) -> str:
        """Get user email."""
        return self._email
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self._user_id == other._user_id
    
    def __hash__(self) -> int:
        return hash(self._user_id)
    
    def __repr__(self) -> str:
        return f"User(id={self._user_id}, name={self._name})"
