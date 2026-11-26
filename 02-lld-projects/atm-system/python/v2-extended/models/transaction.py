"""
Transaction model for ATM System.
"""
import uuid
from datetime import datetime
from enums import TransactionType, TransactionStatus
from .account import Account


class Transaction:
    """
    Represents a single ATM transaction.
    
    DESIGN PATTERN: Command Pattern
    - Encapsulates transaction as an object
    - execute() method performs the action
    """
    
    def __init__(self, tx_type: TransactionType, amount: float, account: Account):
        self.transaction_id = str(uuid.uuid4())[:8]
        self.tx_type = tx_type
        self.amount = amount
        self.timestamp = datetime.now()
        self.status = TransactionStatus.PENDING
        self._account = account
    
    def execute(self) -> bool:
        """Execute the transaction."""
        success = False
        
        if self.tx_type == TransactionType.BALANCE_INQUIRY:
            print(f"Current Balance: ${self._account.balance:.2f}")
            success = True
        elif self.tx_type == TransactionType.WITHDRAWAL:
            success = self._account.withdraw(self.amount)
            if success:
                print(f"Withdrawn: ${self.amount:.2f}")
        elif self.tx_type == TransactionType.DEPOSIT:
            success = self._account.deposit(self.amount)
            if success:
                print(f"Deposited: ${self.amount:.2f}")
        
        self.status = TransactionStatus.COMPLETED if success else TransactionStatus.FAILED
        return success
    
    def __str__(self) -> str:
        return f"[{self.transaction_id}] {self.tx_type.value}: ${self.amount:.2f} - {self.status.value}"
