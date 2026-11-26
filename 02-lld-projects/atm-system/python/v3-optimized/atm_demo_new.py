#!/usr/bin/env python3
"""ATM v3 Thread-Safe Demo."""
import sys
sys.path.insert(0, '.')

from enums import AccountType
from models import Account, Card
from atm import ATM


def main():
    print("=== ATM System v3 - Thread-Safe Demo ===\n")
    
    account = Account("ACC001", AccountType.CHECKING, 1000.0, "1234")
    card = Card("1234567890123456", "John Doe", account)
    atm = ATM("ATM001", "Main Branch")
    
    atm.insert_card(card)
    atm.authenticate_pin("1234")
    atm.check_balance()
    atm.withdraw(200)
    atm.deposit(50)
    atm.eject_card()
    
    atm.print_transaction_log()
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
