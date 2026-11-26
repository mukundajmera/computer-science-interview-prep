"""
ATM State Pattern implementation.
"""
from abc import ABC, abstractmethod
from enum import Enum


class ATMStateType(Enum):
    IDLE = "IDLE"
    HAS_CARD = "HAS_CARD"
    AUTHENTICATED = "AUTHENTICATED"
    TRANSACTION = "TRANSACTION"


class ATMState(ABC):
    """State interface for ATM State Pattern."""
    
    @abstractmethod
    def insert_card(self, atm, card): pass
    
    @abstractmethod
    def authenticate_pin(self, atm, pin) -> bool: pass
    
    @abstractmethod
    def check_balance(self, atm): pass
    
    @abstractmethod
    def withdraw(self, atm, amount) -> bool: pass
    
    @abstractmethod
    def deposit(self, atm, amount) -> bool: pass
    
    @abstractmethod
    def eject_card(self, atm): pass
    
    @abstractmethod
    def get_state_type(self) -> ATMStateType: pass


class IdleState(ATMState):
    def insert_card(self, atm, card):
        atm._current_card = card
        atm._state = HasCardState()
        print(f"Card inserted: {card.masked_number}")
    
    def authenticate_pin(self, atm, pin) -> bool:
        print("Please insert card first")
        return False
    
    def check_balance(self, atm): print("Please insert card first")
    def withdraw(self, atm, amount) -> bool: return False
    def deposit(self, atm, amount) -> bool: return False
    def eject_card(self, atm): print("No card to eject")
    def get_state_type(self) -> ATMStateType: return ATMStateType.IDLE


class HasCardState(ATMState):
    def insert_card(self, atm, card):
        print("Card already inserted")
    
    def authenticate_pin(self, atm, pin) -> bool:
        account = atm._current_card.linked_account
        if account.is_locked:
            print("Account is locked")
            atm.eject_card()
            return False
        if account.validate_pin(pin):
            atm._current_account = account
            atm._state = AuthenticatedState()
            print("Authentication successful!")
            return True
        print("Invalid PIN")
        return False
    
    def check_balance(self, atm): print("Please authenticate first")
    def withdraw(self, atm, amount) -> bool: return False
    def deposit(self, atm, amount) -> bool: return False
    
    def eject_card(self, atm):
        print(f"Card ejected: {atm._current_card.masked_number}")
        atm._current_card = None
        atm._state = IdleState()
    
    def get_state_type(self) -> ATMStateType: return ATMStateType.HAS_CARD


class AuthenticatedState(ATMState):
    def insert_card(self, atm, card): print("Card already inserted")
    def authenticate_pin(self, atm, pin) -> bool: return True
    
    def check_balance(self, atm):
        from enums import TransactionType
        from models import Transaction
        tx = Transaction(TransactionType.BALANCE_INQUIRY, 0, atm._current_account)
        tx.execute()
        atm._transactions.append(tx)
    
    def withdraw(self, atm, amount) -> bool:
        from enums import TransactionType
        from models import Transaction
        tx = Transaction(TransactionType.WITHDRAWAL, amount, atm._current_account)
        success = tx.execute()
        atm._transactions.append(tx)
        return success
    
    def deposit(self, atm, amount) -> bool:
        from enums import TransactionType
        from models import Transaction
        tx = Transaction(TransactionType.DEPOSIT, amount, atm._current_account)
        success = tx.execute()
        atm._transactions.append(tx)
        return success
    
    def eject_card(self, atm):
        print(f"Card ejected: {atm._current_card.masked_number}")
        atm._current_card = None
        atm._current_account = None
        atm._state = IdleState()
    
    def get_state_type(self) -> ATMStateType: return ATMStateType.AUTHENTICATED
