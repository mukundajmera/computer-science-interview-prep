"""
LinkedIn Connection System - V2 Extended

User, ConnectionRequest, and Skill classes with endorsement support.
"""
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Set, List, Dict


class RequestStatus(Enum):
    """Status of a connection request."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class Skill:
    """A user skill that can be endorsed by connections."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._endorsers: Set[str] = set()

    @property
    def name(self) -> str:
        return self._name

    def endorse(self, endorser_id: str) -> bool:
        """Add an endorsement. Returns False if already endorsed."""
        if endorser_id in self._endorsers:
            return False
        self._endorsers.add(endorser_id)
        return True

    def get_endorsement_count(self) -> int:
        return len(self._endorsers)


class User:
    """User class representing a LinkedIn member."""
    
    def __init__(self, user_id: str, name: str, email: str, 
                 headline: str = "", company: str = ""):
        if not user_id:
            raise ValueError("User ID cannot be null or empty")
        self._user_id = user_id
        self._name = name
        self._email = email
        self._headline = headline
        self._company = company
        self._connections: Set['User'] = set()
        self._sent_requests: List['ConnectionRequest'] = []
        self._received_requests: List['ConnectionRequest'] = []
        self._skills: Dict[str, Skill] = {}
    
    def add_skill(self, skill_name: str) -> Skill:
        """Add a skill to this user's profile."""
        key = skill_name.lower()
        if key not in self._skills:
            self._skills[key] = Skill(skill_name)
        return self._skills[key]
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Retrieve a skill by name."""
        return self._skills.get(skill_name.lower())
    
    def get_skills(self) -> List[Skill]:
        """Get all skills."""
        return list(self._skills.values())
    
    def add_connection(self, user: 'User') -> None:
        """Add a connection."""
        if user and user != self:
            self._connections.add(user)
    
    def remove_connection(self, user: 'User') -> None:
        """Remove a connection."""
        self._connections.discard(user)
    
    def is_connected_to(self, user: 'User') -> bool:
        """Check if connected to user."""
        return user in self._connections
    
    def get_connections(self) -> Set['User']:
        """Get all connections."""
        return set(self._connections)
    
    def get_connection_count(self) -> int:
        """Get connection count."""
        return len(self._connections)
    
    def get_mutual_connections(self, other: 'User') -> Set['User']:
        """Find mutual connections with another user."""
        if not other:
            return set()
        return self._connections.intersection(other._connections)
    
    def add_sent_request(self, request: 'ConnectionRequest') -> None:
        self._sent_requests.append(request)
    
    def add_received_request(self, request: 'ConnectionRequest') -> None:
        self._received_requests.append(request)
    
    def get_sent_requests(self) -> List['ConnectionRequest']:
        return list(self._sent_requests)
    
    def get_received_requests(self) -> List['ConnectionRequest']:
        return list(self._received_requests)
    
    def get_pending_received_requests(self) -> List['ConnectionRequest']:
        return [r for r in self._received_requests 
                if r.is_pending() and not r.is_expired()]
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._name = value
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def headline(self) -> str:
        return self._headline
    
    @headline.setter
    def headline(self, value: str):
        self._headline = value
    
    @property
    def company(self) -> str:
        return self._company
    
    @company.setter
    def company(self, value: str):
        self._company = value
    
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self._user_id == other._user_id
    
    def __hash__(self):
        return hash(self._user_id)
    
    def __str__(self):
        return f"User({self._user_id}, {self._name})"


class ConnectionRequest:
    """Connection request between two users."""
    
    _counter = 0
    
    def __init__(self, sender: User, receiver: User, message: str = None):
        if not sender or not receiver:
            raise ValueError("Sender and receiver cannot be null")
        if sender == receiver:
            raise ValueError("Cannot send connection request to yourself")
        
        ConnectionRequest._counter += 1
        self._request_id = f"REQ-{ConnectionRequest._counter}"
        self._sender = sender
        self._receiver = receiver
        self._message = message
        self._status = RequestStatus.PENDING
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
    
    def accept(self) -> bool:
        """Accept the connection request."""
        if self._status != RequestStatus.PENDING:
            return False
        if self.is_expired():
            self._status = RequestStatus.EXPIRED
            return False
        
        self._status = RequestStatus.ACCEPTED
        self._updated_at = datetime.now()
        
        # Create bidirectional connection
        self._sender.add_connection(self._receiver)
        self._receiver.add_connection(self._sender)
        return True
    
    def reject(self) -> bool:
        """Reject the connection request."""
        if self._status != RequestStatus.PENDING:
            return False
        
        self._status = RequestStatus.REJECTED
        self._updated_at = datetime.now()
        return True
    
    def withdraw(self) -> bool:
        """Withdraw the connection request."""
        if self._status != RequestStatus.PENDING:
            return False
        
        self._status = RequestStatus.WITHDRAWN
        self._updated_at = datetime.now()
        return True
    
    def is_pending(self) -> bool:
        return self._status == RequestStatus.PENDING
    
    def is_expired(self) -> bool:
        return self._created_at + timedelta(days=30) < datetime.now()
    
    @property
    def request_id(self) -> str:
        return self._request_id
    
    @property
    def sender(self) -> User:
        return self._sender
    
    @property
    def receiver(self) -> User:
        return self._receiver
    
    @property
    def message(self) -> Optional[str]:
        return self._message
    
    @property
    def status(self) -> RequestStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
