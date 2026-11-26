"""
Card model for ATM System.
"""
from .account import Account


class Card:
    """ATM/Debit card linked to an account."""
    
    def __init__(self, card_number: str, holder_name: str, linked_account: Account):
        self.card_number = card_number
        self.holder_name = holder_name
        self.linked_account = linked_account
    
    @property
    def masked_number(self) -> str:
        """Return masked card number for display."""
        return f"XXXX-XXXX-XXXX-{self.card_number[-4:]}"
