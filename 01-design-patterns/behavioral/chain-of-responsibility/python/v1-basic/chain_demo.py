"""
Chain of Responsibility Pattern - Support Ticket Handling
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class SupportTicket:
    issue: str
    severity: int


# Handler Interface
class SupportHandler(ABC):
    def __init__(self):
        self._next: Optional[SupportHandler] = None
    
    def set_next(self, handler: "SupportHandler") -> "SupportHandler":
        self._next = handler
        return handler
    
    def handle(self, ticket: SupportTicket) -> None:
        if self.can_handle(ticket):
            self.process(ticket)
        elif self._next:
            self._next.handle(ticket)
        else:
            print(f"No handler for: {ticket.issue}")
    
    @abstractmethod
    def can_handle(self, ticket: SupportTicket) -> bool:
        pass
    
    @abstractmethod
    def process(self, ticket: SupportTicket) -> None:
        pass


# Concrete Handlers
class FAQHandler(SupportHandler):
    def can_handle(self, ticket: SupportTicket) -> bool:
        return ticket.severity == 1
    
    def process(self, ticket: SupportTicket) -> None:
        print(f"[FAQ Bot] Answered: {ticket.issue}")


class Level1Support(SupportHandler):
    def can_handle(self, ticket: SupportTicket) -> bool:
        return ticket.severity == 2
    
    def process(self, ticket: SupportTicket) -> None:
        print(f"[L1 Support] Resolved: {ticket.issue}")


class Level2Support(SupportHandler):
    def can_handle(self, ticket: SupportTicket) -> bool:
        return ticket.severity == 3
    
    def process(self, ticket: SupportTicket) -> None:
        print(f"[L2 Support] Investigating: {ticket.issue}")


class ManagerSupport(SupportHandler):
    def can_handle(self, ticket: SupportTicket) -> bool:
        return ticket.severity >= 4
    
    def process(self, ticket: SupportTicket) -> None:
        print(f"[Manager] Escalated: {ticket.issue}")


if __name__ == "__main__":
    # Build chain
    faq = FAQHandler()
    faq.set_next(Level1Support()).set_next(Level2Support()).set_next(ManagerSupport())
    
    # Test tickets
    print("=== Support Tickets ===")
    faq.handle(SupportTicket("Password reset", 1))
    faq.handle(SupportTicket("Login issue", 2))
    faq.handle(SupportTicket("System bug", 3))
    faq.handle(SupportTicket("Data breach", 5))
