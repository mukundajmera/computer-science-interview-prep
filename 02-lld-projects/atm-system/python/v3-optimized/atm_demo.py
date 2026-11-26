"""
ATM System - v3 Optimized Implementation

This version adds:
- Thread-safe account operations with locks
- Concurrent transaction handling
- Optimized cash dispensing with strategy pattern
- Session management with timeout
- Comprehensive error handling
- Cash inventory management
"""

from enum import Enum
from typing import Optional, Dict, List, Callable
from datetime import datetime
from abc import ABC, abstractmethod
import uuid
import time
import threading
from concurrent.futures import ThreadPoolExecutor


# ==================== Enums ====================

class AccountType(Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"


class TransactionType(Enum):
    BALANCE_INQUIRY = "BALANCE_INQUIRY"
    WITHDRAWAL = "WITHDRAWAL"
    DEPOSIT = "DEPOSIT"
    TRANSFER = "TRANSFER"
    PIN_CHANGE = "PIN_CHANGE"


class TransactionStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ROLLED_BACK = "ROLLED_BACK"


class Denomination(Enum):
    HUNDRED = 100
    FIFTY = 50
    TWENTY = 20
    TEN = 10


# ==================== Exceptions ====================

class ATMException(Exception):
    """Base exception for ATM operations."""
    pass


class InsufficientBalanceException(ATMException):
    def __init__(self, requested: float, available: float):
        super().__init__(
            f"Insufficient balance. Requested: ${requested:.2f}, Available: ${available:.2f}"
        )


class InsufficientCashException(ATMException):
    def __init__(self, amount: float):
        super().__init__(
            f"ATM cannot dispense ${amount:.2f}. Please try a different amount."
        )


class DailyLimitExceededException(ATMException):
    def __init__(self, remaining: float):
        super().__init__(f"Daily limit exceeded. Remaining limit: ${remaining:.2f}")


class AccountLockedException(ATMException):
    def __init__(self):
        super().__init__(
            "Account is locked due to too many failed PIN attempts. Please contact your bank."
        )


class SessionExpiredException(ATMException):
    def __init__(self):
        super().__init__("Session has expired due to inactivity. Please start again.")


# ==================== Thread-Safe Account ====================

class Account:
    MAX_FAILED_ATTEMPTS = 3
    DAILY_LIMIT = 3000.0
    TRANSACTION_LIMIT = 1000.0
    
    def __init__(self, account_number: str, account_type: AccountType,
                 initial_balance: float, pin: str):
        self.account_number = account_number
        self.account_type = account_type
        self._balance = initial_balance
        self._pin_hash = self._hash_pin(pin)
        self._is_locked = False
        self._failed_attempts = 0
        self._daily_withdrawn = 0.0
        self._last_withdrawal_date = datetime.now().date()
        self._transaction_history: List['Transaction'] = []
        self._lock = threading.RLock()
    
    def _hash_pin(self, pin: str) -> str:
        """Simple hash for demonstration - use proper hashing in production."""
        return str(hash(pin))
    
    @property
    def balance(self) -> float:
        with self._lock:
            return self._balance
    
    @property
    def is_locked(self) -> bool:
        return self._is_locked
    
    def validate_pin(self, input_pin: str) -> bool:
        """Validate PIN and track failed attempts."""
        if self._is_locked:
            raise AccountLockedException()
        
        if self._pin_hash == self._hash_pin(input_pin):
            self._failed_attempts = 0
            return True
        else:
            self._failed_attempts += 1
            if self._failed_attempts >= self.MAX_FAILED_ATTEMPTS:
                self._is_locked = True
                raise AccountLockedException()
            return False
    
    def _reset_daily_limit_if_new_day(self) -> None:
        """Reset daily withdrawal limit if it's a new day."""
        today = datetime.now().date()
        if today != self._last_withdrawal_date:
            self._daily_withdrawn = 0.0
            self._last_withdrawal_date = today
    
    def withdraw(self, amount: float) -> None:
        """Withdraw amount from account (thread-safe)."""
        with self._lock:
            self._reset_daily_limit_if_new_day()
            
            if amount <= 0:
                raise ATMException("Invalid amount")
            if amount > self.TRANSACTION_LIMIT:
                raise ATMException(f"Amount exceeds transaction limit of ${self.TRANSACTION_LIMIT}")
            if amount > self._balance:
                raise InsufficientBalanceException(amount, self._balance)
            if self._daily_withdrawn + amount > self.DAILY_LIMIT:
                raise DailyLimitExceededException(self.DAILY_LIMIT - self._daily_withdrawn)
            
            self._balance -= amount
            self._daily_withdrawn += amount
    
    def deposit(self, amount: float) -> None:
        """Deposit amount to account (thread-safe)."""
        with self._lock:
            if amount <= 0:
                raise ATMException("Invalid amount")
            self._balance += amount
    
    def change_pin(self, old_pin: str, new_pin: str) -> bool:
        """Change account PIN."""
        with self._lock:
            if not self.validate_pin(old_pin):
                return False
            if not new_pin or len(new_pin) != 4 or not new_pin.isdigit():
                return False
            self._pin_hash = self._hash_pin(new_pin)
            return True
    
    def add_transaction(self, transaction: 'Transaction') -> None:
        """Add transaction to history."""
        self._transaction_history.append(transaction)
    
    def get_recent_transactions(self, count: int = 5) -> List['Transaction']:
        """Get recent transactions."""
        return self._transaction_history[-count:]
    
    def get_remaining_daily_limit(self) -> float:
        """Get remaining daily withdrawal limit."""
        self._reset_daily_limit_if_new_day()
        return self.DAILY_LIMIT - self._daily_withdrawn


# ==================== Card ====================

class Card:
    def __init__(self, card_number: str, holder_name: str):
        self.card_number = card_number
        self.holder_name = holder_name
        self._linked_accounts: List[Account] = []
        self._is_retained = False
    
    def link_account(self, account: Account) -> None:
        """Link an account to this card."""
        self._linked_accounts.append(account)
    
    @property
    def linked_accounts(self) -> List[Account]:
        return list(self._linked_accounts)
    
    @property
    def primary_account(self) -> Optional[Account]:
        return self._linked_accounts[0] if self._linked_accounts else None
    
    @property
    def masked_number(self) -> str:
        return f"XXXX-XXXX-XXXX-{self.card_number[-4:]}"
    
    def retain(self) -> None:
        """Retain the card."""
        self._is_retained = True
    
    @property
    def is_retained(self) -> bool:
        return self._is_retained


# ==================== Cash Dispensing Strategy ====================

class DispensingStrategy(ABC):
    @abstractmethod
    def calculate_dispense(self, amount: int, 
                          inventory: Dict[Denomination, int]) -> Dict[Denomination, int]:
        """Calculate bills to dispense."""
        pass


class MinimumBillsStrategy(DispensingStrategy):
    def calculate_dispense(self, amount: int,
                          inventory: Dict[Denomination, int]) -> Dict[Denomination, int]:
        """Dispense using minimum number of bills."""
        result: Dict[Denomination, int] = {}
        remaining = amount
        
        # Sort denominations by value descending
        for denom in sorted(Denomination, key=lambda d: d.value, reverse=True):
            available = inventory.get(denom, 0)
            needed = remaining // denom.value
            to_use = min(needed, available)
            
            if to_use > 0:
                result[denom] = to_use
                remaining -= to_use * denom.value
        
        if remaining > 0:
            raise InsufficientCashException(amount)
        
        return result


# ==================== Cash Dispenser ====================

class CashDispenser:
    def __init__(self, strategy: DispensingStrategy):
        self._inventory: Dict[Denomination, int] = {d: 100 for d in Denomination}
        self._strategy = strategy
        self._lock = threading.Lock()
    
    def dispense(self, amount: int) -> Dict[Denomination, int]:
        """Dispense cash (thread-safe)."""
        with self._lock:
            to_dispense = self._strategy.calculate_dispense(amount, self._inventory)
            
            # Update inventory
            for denom, count in to_dispense.items():
                self._inventory[denom] -= count
            
            return to_dispense
    
    def can_dispense(self, amount: int) -> bool:
        """Check if amount can be dispensed."""
        with self._lock:
            try:
                self._strategy.calculate_dispense(amount, self._inventory)
                return True
            except InsufficientCashException:
                return False
    
    def add_cash(self, denomination: Denomination, count: int) -> None:
        """Add cash to inventory."""
        with self._lock:
            self._inventory[denomination] += count
    
    def get_total_cash(self) -> int:
        """Get total cash in ATM."""
        with self._lock:
            return sum(d.value * c for d, c in self._inventory.items())
    
    def get_inventory(self) -> Dict[Denomination, int]:
        """Get current inventory."""
        with self._lock:
            return dict(self._inventory)


# ==================== Session Management ====================

class Session:
    SESSION_TIMEOUT_MS = 120_000  # 2 minutes
    
    def __init__(self, card: Card):
        self.session_id = str(uuid.uuid4())[:8]
        self.card = card
        self._current_account = card.primary_account
        self._start_time = time.time() * 1000
        self._last_activity_time = self._start_time
        self._is_active = True
    
    @property
    def current_account(self) -> Optional[Account]:
        return self._current_account
    
    @current_account.setter
    def current_account(self, account: Account) -> None:
        self._current_account = account
        self.update_activity()
    
    def update_activity(self) -> None:
        """Update last activity time."""
        self._last_activity_time = time.time() * 1000
    
    def is_expired(self) -> bool:
        """Check if session has expired."""
        return (time.time() * 1000 - self._last_activity_time) > self.SESSION_TIMEOUT_MS
    
    @property
    def is_active(self) -> bool:
        return self._is_active and not self.is_expired()
    
    def end(self) -> None:
        """End the session."""
        self._is_active = False
    
    def get_duration_seconds(self) -> float:
        """Get session duration in seconds."""
        return (time.time() * 1000 - self._start_time) / 1000


# ==================== Transactions ====================

class Transaction(ABC):
    def __init__(self, trans_type: TransactionType, account: Account):
        self.transaction_id = str(uuid.uuid4())[:8]
        self.type = trans_type
        self.timestamp = datetime.now()
        self.status = TransactionStatus.PENDING
        self.account = account
        self.amount = 0.0
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the transaction."""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback the transaction."""
        pass
    
    def __str__(self) -> str:
        return (f"[{self.timestamp.strftime('%m/%d %H:%M:%S')}] "
                f"{self.transaction_id} {self.type.value}: ${self.amount:.2f} - {self.status.value}")


class WithdrawalTransaction(Transaction):
    def __init__(self, account: Account, amount: float, cash_dispenser: CashDispenser):
        super().__init__(TransactionType.WITHDRAWAL, account)
        self.amount = amount
        self._cash_dispenser = cash_dispenser
        self._dispensed_bills: Optional[Dict[Denomination, int]] = None
    
    def execute(self) -> None:
        """Execute withdrawal."""
        if not self._cash_dispenser.can_dispense(int(self.amount)):
            self.status = TransactionStatus.FAILED
            raise InsufficientCashException(self.amount)
        
        self.account.withdraw(self.amount)
        
        try:
            self._dispensed_bills = self._cash_dispenser.dispense(int(self.amount))
            self.status = TransactionStatus.COMPLETED
            self.account.add_transaction(self)
            
            print(f"Withdrawn: ${self.amount:.2f}")
            print("Dispensing:")
            for denom, count in self._dispensed_bills.items():
                print(f"  {count} x ${denom.value} bills")
            print(f"Remaining Balance: ${self.account.balance:.2f}")
            
        except InsufficientCashException as e:
            self.account.deposit(self.amount)
            self.status = TransactionStatus.FAILED
            raise
    
    def rollback(self) -> None:
        """Rollback withdrawal."""
        if self.status == TransactionStatus.COMPLETED:
            self.account.deposit(self.amount)
            self.status = TransactionStatus.ROLLED_BACK


class DepositTransaction(Transaction):
    def __init__(self, account: Account, amount: float):
        super().__init__(TransactionType.DEPOSIT, account)
        self.amount = amount
    
    def execute(self) -> None:
        """Execute deposit."""
        self.account.deposit(self.amount)
        self.status = TransactionStatus.COMPLETED
        self.account.add_transaction(self)
        
        print(f"Deposited: ${self.amount:.2f}")
        print(f"New Balance: ${self.account.balance:.2f}")
    
    def rollback(self) -> None:
        """Rollback deposit."""
        if self.status == TransactionStatus.COMPLETED:
            self.account.withdraw(self.amount)
            self.status = TransactionStatus.ROLLED_BACK


class TransferTransaction(Transaction):
    def __init__(self, source: Account, destination: Account, amount: float):
        super().__init__(TransactionType.TRANSFER, source)
        self._destination = destination
        self.amount = amount
    
    def execute(self) -> None:
        """Execute transfer (with deadlock prevention)."""
        # Lock accounts in consistent order
        accounts = sorted([self.account, self._destination], 
                         key=lambda a: (hash(a.account_number), a.account_number))
        
        with accounts[0]._lock:
            with accounts[1]._lock:
                self.account.withdraw(self.amount)
                try:
                    self._destination.deposit(self.amount)
                except ATMException:
                    self.account.deposit(self.amount)
                    raise
                
                self.status = TransactionStatus.COMPLETED
                self.account.add_transaction(self)
                
                print(f"Transferred: ${self.amount:.2f} to {self._destination.account_number}")
                print(f"Your new balance: ${self.account.balance:.2f}")
    
    def rollback(self) -> None:
        """Rollback transfer."""
        if self.status == TransactionStatus.COMPLETED:
            self._destination.withdraw(self.amount)
            self.account.deposit(self.amount)
            self.status = TransactionStatus.ROLLED_BACK


# ==================== ATM ====================

class ATM:
    def __init__(self, atm_id: str, location: str):
        self.atm_id = atm_id
        self.location = location
        self._cash_dispenser = CashDispenser(MinimumBillsStrategy())
        self._current_session: Optional[Session] = None
        self._transaction_log: List[Transaction] = []
        self._session_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=4)
    
    def insert_card(self, card: Card) -> None:
        """Insert card and start session."""
        with self._session_lock:
            if self._current_session and self._current_session.is_active:
                raise ATMException("Another session is in progress")
            
            if card.is_retained:
                raise ATMException("This card has been retained. Please contact your bank.")
            
            self._current_session = Session(card)
            print(f"Card inserted: {card.masked_number}")
            print(f"Session started: {self._current_session.session_id}")
    
    def authenticate_pin(self, pin: str) -> bool:
        """Authenticate user with PIN."""
        self._check_session()
        
        account = self._current_session.current_account
        try:
            if account.validate_pin(pin):
                self._current_session.update_activity()
                print("PIN verified successfully")
                return True
            else:
                print("Incorrect PIN. Please try again.")
                return False
        except AccountLockedException as e:
            self._current_session.card.retain()
            self._end_session()
            raise
    
    def select_account(self, account: Account) -> None:
        """Select account for transactions."""
        self._check_session()
        
        if account not in self._current_session.card.linked_accounts:
            raise ATMException("Account not linked to this card")
        
        self._current_session.current_account = account
        print(f"Selected account: {account.account_number} ({account.account_type.value})")
    
    def check_balance(self) -> None:
        """Display account balance."""
        self._check_session()
        
        account = self._current_session.current_account
        self._current_session.update_activity()
        
        print("\n=== Balance Inquiry ===")
        print(f"Account: {account.account_number} ({account.account_type.value})")
        print(f"Current Balance: ${account.balance:.2f}")
        print(f"Daily Withdrawal Remaining: ${account.get_remaining_daily_limit():.2f}")
    
    def withdraw(self, amount: float) -> None:
        """Withdraw cash."""
        self._check_session()
        
        account = self._current_session.current_account
        transaction = WithdrawalTransaction(account, amount, self._cash_dispenser)
        
        transaction.execute()
        self._transaction_log.append(transaction)
        self._current_session.update_activity()
    
    def deposit(self, amount: float) -> None:
        """Deposit cash."""
        self._check_session()
        
        account = self._current_session.current_account
        transaction = DepositTransaction(account, amount)
        
        transaction.execute()
        self._transaction_log.append(transaction)
        self._current_session.update_activity()
    
    def transfer(self, destination: Account, amount: float) -> None:
        """Transfer funds."""
        self._check_session()
        
        source = self._current_session.current_account
        transaction = TransferTransaction(source, destination, amount)
        
        transaction.execute()
        self._transaction_log.append(transaction)
        self._current_session.update_activity()
    
    def show_transaction_history(self) -> None:
        """Display recent transactions."""
        self._check_session()
        
        account = self._current_session.current_account
        history = account.get_recent_transactions(5)
        
        print("\n=== Recent Transactions ===")
        if not history:
            print("No transactions found")
        else:
            for t in history:
                print(t)
        
        self._current_session.update_activity()
    
    def eject_card(self) -> None:
        """Eject card and end session."""
        with self._session_lock:
            if self._current_session:
                duration = self._current_session.get_duration_seconds()
                print(f"Card ejected. Session duration: {duration:.1f} seconds")
                print(f"Thank you for using ATM {self.atm_id}")
                self._end_session()
    
    def _check_session(self) -> None:
        """Verify session is valid."""
        if not self._current_session:
            raise ATMException("Please insert a card first")
        if self._current_session.is_expired():
            self._end_session()
            raise SessionExpiredException()
        if not self._current_session.is_active:
            raise ATMException("Session is not active")
    
    def _end_session(self) -> None:
        """End current session."""
        if self._current_session:
            self._current_session.end()
            self._current_session = None
    
    def get_total_cash(self) -> int:
        """Get total cash in ATM."""
        return self._cash_dispenser.get_total_cash()
    
    def get_cash_inventory(self) -> Dict[Denomination, int]:
        """Get cash inventory."""
        return self._cash_dispenser.get_inventory()
    
    def shutdown(self) -> None:
        """Shutdown ATM executor."""
        self._executor.shutdown(wait=True)


# ==================== Demo ====================

def main():
    print("=== ATM System v3 - Optimized Demo ===\n")
    
    # Create accounts
    checking = Account("CHK001", AccountType.CHECKING, 2500.0, "1234")
    savings = Account("SAV001", AccountType.SAVINGS, 10000.0, "1234")
    
    # Create card with multiple accounts
    card = Card("1234567890123456", "John Doe")
    card.link_account(checking)
    card.link_account(savings)
    
    # Create ATM
    atm = ATM("ATM001", "Main Street Branch")
    
    try:
        # Show ATM cash inventory
        print("ATM Cash Inventory:")
        for denom, count in atm.get_cash_inventory().items():
            print(f"  ${denom.value} bills: {count}")
        print(f"Total: ${atm.get_total_cash()}\n")
        
        atm.insert_card(card)
        atm.authenticate_pin("1234")
        
        # Check balance
        atm.check_balance()
        
        # Withdraw
        print("\n[Withdrawing $270]")
        atm.withdraw(270)
        
        # Deposit
        print("\n[Depositing $150]")
        atm.deposit(150)
        
        # Switch to savings
        print("\n[Switching to Savings Account]")
        atm.select_account(savings)
        atm.check_balance()
        
        # Transfer
        print("\n[Transferring $500 to Checking]")
        atm.transfer(checking, 500)
        
        # Show history
        atm.show_transaction_history()
        
        # Eject card
        print()
        atm.eject_card()
        
        # Demo: Concurrent operations
        print("\n--- Concurrent Transaction Demo ---")
        demo_concurrent_transactions()
        
    except ATMException as e:
        print(f"ATM Error: {e}")
    finally:
        atm.shutdown()
    
    print("\n=== Demo Complete ===")


def demo_concurrent_transactions():
    """Demonstrate concurrent transaction handling."""
    acc1 = Account("ACC001", AccountType.CHECKING, 1000.0, "1111")
    acc2 = Account("ACC002", AccountType.CHECKING, 1000.0, "2222")
    
    results = []
    lock = threading.Lock()
    
    def transfer(source, dest, amount):
        try:
            t = TransferTransaction(source, dest, amount)
            t.execute()
            with lock:
                results.append(f"Transfer ${amount} from {source.account_number} to {dest.account_number}: SUCCESS")
        except ATMException as e:
            with lock:
                results.append(f"Transfer failed: {e}")
    
    threads = []
    for i in range(2):
        amount = 100 * (i + 1)
        t1 = threading.Thread(target=transfer, args=(acc1, acc2, amount))
        t2 = threading.Thread(target=transfer, args=(acc2, acc1, amount))
        threads.extend([t1, t2])
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    for r in results:
        print(r)
    
    print(f"Final balance ACC001: ${acc1.balance:.2f}")
    print(f"Final balance ACC002: ${acc2.balance:.2f}")


if __name__ == "__main__":
    main()
