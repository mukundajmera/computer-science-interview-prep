"""
ATM System - v1 Basic Implementation

This version includes:
- Basic account management
- PIN authentication
- Balance inquiry, withdrawal, deposit
- Simple ATM state management
"""

from enum import Enum
from typing import Optional, List
from datetime import datetime
import uuid


# ==================== Enums ====================

class AccountType(Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"


class TransactionType(Enum):
    BALANCE_INQUIRY = "BALANCE_INQUIRY"
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"


class TransactionStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ==================== Account ====================

class Account:
    MAX_FAILED_ATTEMPTS = 3
    
    def __init__(self, account_number: str, account_type: AccountType, 
                 initial_balance: float, pin: str):
        self.account_number = account_number
        self.account_type = account_type
        self._balance = initial_balance
        self._pin = pin
        self._is_locked = False
        self._failed_attempts = 0
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @property
    def is_locked(self) -> bool:
        return self._is_locked
    
    def validate_pin(self, input_pin: str) -> bool:
        """Validate PIN and track failed attempts."""
        if self._is_locked:
            return False
        
        if self._pin == input_pin:
            self._failed_attempts = 0
            return True
        else:
            self._failed_attempts += 1
            if self._failed_attempts >= self.MAX_FAILED_ATTEMPTS:
                self._is_locked = True
                print("Account locked due to too many failed attempts!")
            return False
    
    def withdraw(self, amount: float) -> bool:
        """Withdraw amount from account."""
        if amount <= 0:
            print("Invalid amount")
            return False
        if amount > self._balance:
            print("Insufficient balance")
            return False
        
        self._balance -= amount
        return True
    
    def deposit(self, amount: float) -> bool:
        """Deposit amount to account."""
        if amount <= 0:
            print("Invalid amount")
            return False
        
        self._balance += amount
        return True
    
    def change_pin(self, old_pin: str, new_pin: str) -> bool:
        """Change account PIN."""
        if self.validate_pin(old_pin):
            self._pin = new_pin
            print("PIN changed successfully")
            return True
        else:
            print("Invalid current PIN")
            return False
    
    def __str__(self) -> str:
        return f"Account[{self.account_number}, {self.account_type.value}, Balance: ${self._balance:.2f}]"


# ==================== Card ====================

class Card:
    def __init__(self, card_number: str, holder_name: str, linked_account: Account):
        self.card_number = card_number
        self.holder_name = holder_name
        self.linked_account = linked_account
    
    @property
    def masked_number(self) -> str:
        return f"XXXX-XXXX-XXXX-{self.card_number[-4:]}"


# ==================== Transaction ====================

class Transaction:
    def __init__(self, trans_type: TransactionType, amount: float, account: Account):
        self.transaction_id = str(uuid.uuid4())[:8]
        self.type = trans_type
        self.amount = amount
        self.timestamp = datetime.now()
        self.status = TransactionStatus.PENDING
        self.account = account
    
    def execute(self) -> bool:
        """Execute the transaction."""
        success = False
        
        if self.type == TransactionType.BALANCE_INQUIRY:
            print(f"Current Balance: ${self.account.balance:.2f}")
            success = True
        elif self.type == TransactionType.WITHDRAWAL:
            success = self.account.withdraw(self.amount)
            if success:
                print(f"Withdrawn: ${self.amount:.2f}")
        elif self.type == TransactionType.DEPOSIT:
            success = self.account.deposit(self.amount)
            if success:
                print(f"Deposited: ${self.amount:.2f}")
        
        self.status = TransactionStatus.COMPLETED if success else TransactionStatus.FAILED
        return success
    
    def __str__(self) -> str:
        return f"[{self.transaction_id}] {self.type.value}: ${self.amount:.2f} - {self.status.value}"


# ==================== ATM ====================

class ATM:
    def __init__(self, atm_id: str, location: str):
        self.atm_id = atm_id
        self.location = location
        self._current_card: Optional[Card] = None
        self._is_authenticated = False
        self._transaction_log: List[Transaction] = []
    
    def insert_card(self, card: Card) -> bool:
        """Insert a card into the ATM."""
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
        """Display account balance."""
        if not self._is_authenticated:
            print("Please authenticate first")
            return
        
        transaction = Transaction(
            TransactionType.BALANCE_INQUIRY, 
            0, 
            self._current_card.linked_account
        )
        transaction.execute()
        self._transaction_log.append(transaction)
    
    def withdraw(self, amount: float) -> bool:
        """Withdraw cash from account."""
        if not self._is_authenticated:
            print("Please authenticate first")
            return False
        
        transaction = Transaction(
            TransactionType.WITHDRAWAL, 
            amount, 
            self._current_card.linked_account
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
            TransactionType.DEPOSIT, 
            amount, 
            self._current_card.linked_account
        )
        success = transaction.execute()
        self._transaction_log.append(transaction)
        return success
    
    def eject_card(self) -> None:
        """Eject the card from ATM."""
        if self._current_card is not None:
            print(f"Card ejected: {self._current_card.masked_number}")
            self._current_card = None
            self._is_authenticated = False
    
    def print_transaction_log(self) -> None:
        """Print all transactions."""
        print("\n=== Transaction Log ===")
        for t in self._transaction_log:
            print(t)


# ==================== Demo ====================

def main():
    print("=== ATM System v1 - Basic Demo ===\n")
    
    # Create account and card
    account = Account("ACC001", AccountType.CHECKING, 1000.0, "1234")
    card = Card("1234567890123456", "John Doe", account)
    
    # Create ATM
    atm = ATM("ATM001", "Main Street Branch")
    
    # Demo: Normal flow
    print("--- Normal Transaction Flow ---")
    atm.insert_card(card)
    atm.authenticate_pin("1234")
    atm.check_balance()
    atm.withdraw(200)
    atm.check_balance()
    atm.deposit(50)
    atm.check_balance()
    atm.eject_card()
    
    # Demo: Failed authentication
    print("\n--- Failed Authentication Demo ---")
    account2 = Account("ACC002", AccountType.SAVINGS, 500.0, "5678")
    card2 = Card("9876543210987654", "Jane Smith", account2)
    
    atm.insert_card(card2)
    atm.authenticate_pin("0000")  # Wrong PIN
    atm.authenticate_pin("1111")  # Wrong PIN
    atm.authenticate_pin("2222")  # Wrong PIN - should lock
    atm.eject_card()
    
    # Print transaction log
    atm.print_transaction_log()
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
