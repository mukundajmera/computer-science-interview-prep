"""
ATM controller for ATM System.
"""
from typing import List, Optional
from enums import TransactionType
from models import Account, Card, Transaction


class ATM:
    """
    Main ATM machine controller.
    
    FLOW:
    1. insert_card() → Card inserted
    2. authenticate_pin() → User authenticated  
    3. check_balance() / withdraw() / deposit() → Operations
    4. eject_card() → Session end
    """
    
    def __init__(self, atm_id: str, location: str):
        self.atm_id = atm_id
        self.location = location
        self._current_card: Optional[Card] = None
        self._is_authenticated = False
        self._transaction_log: List[Transaction] = []
    
    def insert_card(self, card: Card) -> bool:
        """Insert card into ATM."""
        if self._current_card is not None:
            print("Another card is already inserted")
            return False
        self._current_card = card
        print(f"Card inserted: {card.masked_number}")
        return True
    
    def authenticate_pin(self, pin: str) -> bool:
        """Authenticate user with PIN."""
        if self._current_card is None:
            print("Please insert a card first")
            return False
        
        account = self._current_card.linked_account
        if account.is_locked:
            print("Account is locked. Please contact bank.")
            self.eject_card()
            return False
        
        if account.validate_pin(pin):
            self._is_authenticated = True
            print("Authentication successful!")
            return True
        else:
            print("Invalid PIN")
            if account.is_locked:
                self.eject_card()
            return False
    
    def check_balance(self) -> None:
        """Check account balance."""
        if not self._is_authenticated:
            print("Please authenticate first")
            return
        transaction = Transaction(
            TransactionType.BALANCE_INQUIRY, 0, self._current_card.linked_account
        )
        transaction.execute()
        self._transaction_log.append(transaction)
    
    def withdraw(self, amount: float) -> bool:
        """Withdraw cash from account."""
        if not self._is_authenticated:
            print("Please authenticate first")
            return False
        transaction = Transaction(
            TransactionType.WITHDRAWAL, amount, self._current_card.linked_account
        )
        success = transaction.execute()
        self._transaction_log.append(transaction)
        return success
    
    def deposit(self, amount: float) -> bool:
        """Deposit cash to account."""
        if not self._is_authenticated:
            print("Please authenticate first")
            return False
        transaction = Transaction(
            TransactionType.DEPOSIT, amount, self._current_card.linked_account
        )
        success = transaction.execute()
        self._transaction_log.append(transaction)
        return success
    
    def eject_card(self) -> None:
        """Eject card and end session."""
        if self._current_card is not None:
            print(f"Card ejected: {self._current_card.masked_number}")
            self._current_card = None
            self._is_authenticated = False
    
    def print_transaction_log(self) -> None:
        """Print all transactions."""
        print("\n=== Transaction Log ===")
        for t in self._transaction_log:
            print(t)
