#!/usr/bin/env python3
"""
ATM System Demo - v1 Basic.

Usage:
    cd python/v1-basic
    python atm_demo_new.py
"""
import sys
sys.path.insert(0, '.')

from enums import AccountType
from models import Account, Card
from atm import ATM


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
