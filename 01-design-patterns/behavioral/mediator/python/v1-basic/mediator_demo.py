"""
Mediator Pattern - Chat Room
"""
from abc import ABC, abstractmethod
from typing import List


# Mediator Interface
class ChatMediator(ABC):
    @abstractmethod
    def send_message(self, message: str, sender: "User") -> None:
        pass
    
    @abstractmethod
    def add_user(self, user: "User") -> None:
        pass


# Concrete Mediator
class ChatRoom(ChatMediator):
    def __init__(self):
        self._users: List[User] = []
    
    def add_user(self, user: "User") -> None:
        self._users.append(user)
        print(f"{user.name} joined the chat")
    
    def send_message(self, message: str, sender: "User") -> None:
        for user in self._users:
            if user != sender:
                user.receive(message, sender.name)


# Colleague
class User(ABC):
    def __init__(self, mediator: ChatMediator, name: str):
        self._mediator = mediator
        self.name = name
    
    @abstractmethod
    def send(self, message: str) -> None:
        pass
    
    @abstractmethod
    def receive(self, message: str, from_user: str) -> None:
        pass


# Concrete Colleague
class ChatUser(User):
    def send(self, message: str) -> None:
        print(f"{self.name} sends: {message}")
        self._mediator.send_message(message, self)
    
    def receive(self, message: str, from_user: str) -> None:
        print(f"{self.name} received from {from_user}: {message}")


if __name__ == "__main__":
    chat_room = ChatRoom()
    
    alice = ChatUser(chat_room, "Alice")
    bob = ChatUser(chat_room, "Bob")
    charlie = ChatUser(chat_room, "Charlie")
    
    chat_room.add_user(alice)
    chat_room.add_user(bob)
    chat_room.add_user(charlie)
    
    print("\n=== Chat ===")
    alice.send("Hello everyone!")
    print()
    bob.send("Hi Alice!")
