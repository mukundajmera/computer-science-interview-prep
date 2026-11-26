"""ATM v3 Thread-Safe with threading Lock."""
from typing import List, Optional
from threading import Lock
from states import IdleState, ATMState
from models import Card, Account, Transaction


class ATM:
    """
    ATM v3 Thread-Safe.
    
    Uses threading.Lock for transaction safety.
    """
    
    def __init__(self, atm_id: str, location: str):
        self.atm_id = atm_id
        self.location = location
        self._state: ATMState = IdleState()
        self._current_card: Optional[Card] = None
        self._current_account: Optional[Account] = None
        self._transactions: List[Transaction] = []
        self._lock = Lock()
    
    def insert_card(self, card: Card): self._state.insert_card(self, card)
    def authenticate_pin(self, pin: str) -> bool: return self._state.authenticate_pin(self, pin)
    
    def check_balance(self):
        with self._lock:
            self._state.check_balance(self)
    
    def withdraw(self, amount: float) -> bool:
        with self._lock:
            return self._state.withdraw(self, amount)
    
    def deposit(self, amount: float) -> bool:
        with self._lock:
            return self._state.deposit(self, amount)
    
    def eject_card(self): self._state.eject_card(self)
    
    @property
    def state_type(self): return self._state.get_state_type()
    
    def print_transaction_log(self):
        print("\n=== Transaction Log ===")
        for t in self._transactions:
            print(t)
