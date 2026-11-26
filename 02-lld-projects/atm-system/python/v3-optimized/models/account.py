"""
Account model for ATM System.
"""
from enums import AccountType


class Account:
    """
    Bank account with balance and PIN management.
    
    SECURITY: Locks after 3 failed PIN attempts.
    """
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
        """
        Validate PIN with lockout protection.
        
        Returns:
            True if PIN is correct, False otherwise.
        """
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
        """Withdraw money from account."""
        if amount <= 0:
            print("Invalid amount")
            return False
        if amount > self._balance:
            print("Insufficient balance")
            return False
        self._balance -= amount
        return True
    
    def deposit(self, amount: float) -> bool:
        """Deposit money to account."""
        if amount <= 0:
            print("Invalid amount")
            return False
        self._balance += amount
        return True
    
    def change_pin(self, old_pin: str, new_pin: str) -> None:
        """Change account PIN."""
        if self.validate_pin(old_pin):
            self._pin = new_pin
            print("PIN changed successfully")
        else:
            print("Invalid current PIN")
    
    def __str__(self) -> str:
        return f"Account[{self.account_number}, {self.account_type.value}, Balance: ${self._balance:.2f}]"
