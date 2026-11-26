"""
LinkedIn Connection System - V1 Basic

NetworkService class - Facade for connection operations.
"""
from typing import Dict, List, Set, Optional
from user import User, ConnectionRequest


class NetworkService:
    """Main network service using Singleton pattern."""
    
    _instance: Optional['NetworkService'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._users: Dict[str, User] = {}
        self._pending_requests: Dict[str, ConnectionRequest] = {}
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'NetworkService':
        return cls()
    
    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None
    
    def register_user(self, user: User) -> bool:
        if not user or user.user_id in self._users:
            return False
        self._users[user.user_id] = user
        return True
    
    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        return list(self._users.values())
    
    def send_connection_request(self, sender_id: str, receiver_id: str, 
                                message: str = None) -> Optional[ConnectionRequest]:
        sender = self._users.get(sender_id)
        receiver = self._users.get(receiver_id)
        
        if not sender or not receiver:
            print("User not found")
            return None
        
        if sender == receiver:
            print("Cannot send connection request to yourself")
            return None
        
        if sender.is_connected_to(receiver):
            print("Already connected")
            return None
        
        # Check for existing pending request
        for req in sender.get_sent_requests():
            if req.receiver == receiver and req.is_pending():
                print("Pending request already exists")
                return None
        
        request = ConnectionRequest(sender, receiver, message)
        sender.add_sent_request(request)
        receiver.add_received_request(request)
        self._pending_requests[request.request_id] = request
        
        print(f"{sender.name} sent connection request to {receiver.name}")
        return request
    
    def accept_request(self, request_id: str) -> bool:
        request = self._pending_requests.get(request_id)
        if not request:
            print("Request not found")
            return False
        
        if request.accept():
            del self._pending_requests[request_id]
            print(f"{request.receiver.name} accepted {request.sender.name}'s request")
            return True
        return False
    
    def reject_request(self, request_id: str) -> bool:
        request = self._pending_requests.get(request_id)
        if not request:
            return False
        
        if request.reject():
            del self._pending_requests[request_id]
            return True
        return False
    
    def remove_connection(self, user_id1: str, user_id2: str) -> bool:
        user1 = self._users.get(user_id1)
        user2 = self._users.get(user_id2)
        
        if not user1 or not user2:
            return False
        
        user1.remove_connection(user2)
        user2.remove_connection(user1)
        return True
    
    def get_connections(self, user_id: str) -> Set[User]:
        user = self._users.get(user_id)
        if not user:
            return set()
        return user.get_connections()
    
    def get_mutual_connections(self, user_id1: str, user_id2: str) -> Set[User]:
        user1 = self._users.get(user_id1)
        user2 = self._users.get(user_id2)
        
        if not user1 or not user2:
            return set()
        return user1.get_mutual_connections(user2)
    
    def are_connected(self, user_id1: str, user_id2: str) -> bool:
        user1 = self._users.get(user_id1)
        user2 = self._users.get(user_id2)
        
        if not user1 or not user2:
            return False
        return user1.is_connected_to(user2)
    
    def get_user_count(self) -> int:
        return len(self._users)
    
    def get_total_connection_count(self) -> int:
        total = sum(u.get_connection_count() for u in self._users.values())
        return total // 2  # Bidirectional


# Demo
if __name__ == "__main__":
    print("=== LinkedIn Connection Demo ===\n")
    
    network = NetworkService.get_instance()
    
    alice = User("U001", "Alice", "alice@email.com", "Software Engineer", "Tech Corp")
    bob = User("U002", "Bob", "bob@email.com", "Product Manager", "StartupX")
    charlie = User("U003", "Charlie", "charlie@email.com", "Data Scientist", "DataCo")
    
    network.register_user(alice)
    network.register_user(bob)
    network.register_user(charlie)
    
    req1 = network.send_connection_request("U001", "U002", "Hi Bob!")
    req2 = network.send_connection_request("U001", "U003")
    req3 = network.send_connection_request("U002", "U003")
    
    network.accept_request(req1.request_id)
    network.accept_request(req2.request_id)
    network.accept_request(req3.request_id)
    
    print(f"\nAlice's connections: {len(network.get_connections('U001'))}")
    print(f"Mutual connections (Alice, Bob): {len(network.get_mutual_connections('U001', 'U002'))}")
    
    NetworkService.reset_instance()
    print("\n=== Demo Complete ===")
