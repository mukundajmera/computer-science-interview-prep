"""
ATM System Tests - unittest

Tests for all versions of the ATM system
"""

import unittest
import sys
import os
import threading
from enum import Enum


# ==================== Minimal Implementation for Testing ====================

class AccountType(Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"


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
        self._lock = threading.Lock()
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @property
    def is_locked(self) -> bool:
        return self._is_locked
    
    def validate_pin(self, input_pin: str) -> bool:
        if self._is_locked:
            return False
        
        if self._pin == input_pin:
            self._failed_attempts = 0
            return True
        else:
            self._failed_attempts += 1
            if self._failed_attempts >= self.MAX_FAILED_ATTEMPTS:
                self._is_locked = True
            return False
    
    def withdraw(self, amount: float) -> bool:
        if amount <= 0 or amount > self._balance:
            return False
        self._balance -= amount
        return True
    
    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            return False
        self._balance += amount
        return True

def transferBetweenAccounts(from_account: Account, to_account: Account, amount: float) -> bool:
    if amount <= 0:
        return False
    
    accounts = sorted([from_account, to_account], key=lambda a: (hash(a.account_number), a.account_number))
    with accounts[0]._lock:
        with accounts[1]._lock:
            if from_account.balance < amount:
                return False
            from_account.withdraw(amount)
            to_account.deposit(amount)
            return True


class Card:
    def __init__(self, card_number: str, linked_account: Account):
        self.card_number = card_number
        self.linked_account = linked_account
    
    @property
    def masked_number(self) -> str:
        return f"XXXX-XXXX-XXXX-{self.card_number[-4:]}"


# ==================== Tests ====================

class TestAccount(unittest.TestCase):
    """Tests for Account class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.account = Account("ACC001", AccountType.CHECKING, 1000.0, "1234")
    
    def test_account_creation(self):
        """Test account is created with correct values."""
        self.assertEqual("ACC001", self.account.account_number)
        self.assertEqual(AccountType.CHECKING, self.account.account_type)
        self.assertEqual(1000.0, self.account.balance)
        self.assertFalse(self.account.is_locked)
    
    def test_valid_pin_authentication(self):
        """Test correct PIN validates successfully."""
        self.assertTrue(self.account.validate_pin("1234"))
    
    def test_invalid_pin_authentication(self):
        """Test incorrect PIN fails validation."""
        self.assertFalse(self.account.validate_pin("0000"))
        self.assertFalse(self.account.is_locked)
    
    def test_account_lock_after_failed_attempts(self):
        """Test account locks after 3 failed PIN attempts."""
        self.account.validate_pin("0000")  # 1st failed
        self.account.validate_pin("1111")  # 2nd failed
        self.assertFalse(self.account.is_locked)
        self.account.validate_pin("2222")  # 3rd failed - should lock
        self.assertTrue(self.account.is_locked)
    
    def test_locked_account_cannot_authenticate(self):
        """Test locked account rejects even correct PIN."""
        # Lock the account
        self.account.validate_pin("0000")
        self.account.validate_pin("1111")
        self.account.validate_pin("2222")
        
        # Even correct PIN should fail
        self.assertFalse(self.account.validate_pin("1234"))
    
    def test_successful_withdrawal(self):
        """Test successful withdrawal updates balance."""
        self.assertTrue(self.account.withdraw(200))
        self.assertEqual(800.0, self.account.balance)
    
    def test_withdrawal_insufficient_balance(self):
        """Test withdrawal fails for insufficient balance."""
        self.assertFalse(self.account.withdraw(1500))
        self.assertEqual(1000.0, self.account.balance)
    
    def test_withdrawal_invalid_amount(self):
        """Test withdrawal fails for invalid amount."""
        self.assertFalse(self.account.withdraw(-50))
        self.assertFalse(self.account.withdraw(0))
        self.assertEqual(1000.0, self.account.balance)
    
    def test_successful_deposit(self):
        """Test successful deposit updates balance."""
        self.assertTrue(self.account.deposit(500))
        self.assertEqual(1500.0, self.account.balance)
    
    def test_deposit_invalid_amount(self):
        """Test deposit fails for invalid amount."""
        self.assertFalse(self.account.deposit(-50))
        self.assertFalse(self.account.deposit(0))
        self.assertEqual(1000.0, self.account.balance)
    
    def test_multiple_transactions(self):
        """Test multiple transactions update balance correctly."""
        self.account.withdraw(200)
        self.account.deposit(150)
        self.account.withdraw(100)
        self.assertEqual(850.0, self.account.balance)


class TestCard(unittest.TestCase):
    """Tests for Card class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.account = Account("ACC001", AccountType.CHECKING, 1000.0, "1234")
        self.card = Card("1234567890123456", self.account)
    
    def test_card_masked_number(self):
        """Test card number is properly masked."""
        self.assertEqual("XXXX-XXXX-XXXX-3456", self.card.masked_number)
    
    def test_card_links_to_account(self):
        """Test card links to correct account."""
        self.assertEqual("ACC001", self.card.linked_account.account_number)


class TestIntegration(unittest.TestCase):
    """Integration tests for ATM operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.account = Account("ACC001", AccountType.CHECKING, 1000.0, "1234")
        self.card = Card("1234567890123456", self.account)
    
    def test_complete_withdrawal_flow(self):
        """Test complete withdrawal flow."""
        # Authenticate
        self.assertTrue(self.account.validate_pin("1234"))
        
        # Check initial balance
        self.assertEqual(1000.0, self.account.balance)
        
        # Withdraw
        self.assertTrue(self.account.withdraw(300))
        self.assertEqual(700.0, self.account.balance)
    
    def test_complete_deposit_flow(self):
        """Test complete deposit flow."""
        # Authenticate
        self.assertTrue(self.account.validate_pin("1234"))
        
        # Deposit
        self.assertTrue(self.account.deposit(500))
        self.assertEqual(1500.0, self.account.balance)
    
    def test_failed_auth_state(self):
        """Test account state after failed authentication."""
        # Lock account
        self.account.validate_pin("0000")
        self.account.validate_pin("1111")
        self.account.validate_pin("2222")
        
        # Account should be locked
        self.assertTrue(self.account.is_locked)
        
        # Cannot authenticate even with correct PIN
        self.assertFalse(self.account.validate_pin("1234"))
    
    def test_withdraw_exact_balance(self):
        """Test withdrawing exact balance amount."""
        self.assertTrue(self.account.withdraw(1000.0))
        self.assertEqual(0.0, self.account.balance)
    
    def test_small_amounts(self):
        """Test small deposit and withdrawal amounts."""
        self.assertTrue(self.account.deposit(0.01))
        self.assertAlmostEqual(1000.01, self.account.balance, places=2)
        
        self.assertTrue(self.account.withdraw(0.01))
        self.assertAlmostEqual(1000.0, self.account.balance, places=2)


class TestConcurrent(unittest.TestCase):
    """Concurrent tests for deadlock and race conditions."""
    def test_concurrent_transfers(self):
        acc1 = Account("ACC1", AccountType.CHECKING, 1000.0, "1234")
        acc2 = Account("ACC2", AccountType.CHECKING, 1000.0, "5678")
        
        def worker(from_acc, to_acc, amount, iterations):
            for _ in range(iterations):
                transferBetweenAccounts(from_acc, to_acc, amount)
                
        threads = []
        # Create 8 worker threads for stress testing
        for i in range(4):
            t1 = threading.Thread(target=worker, args=(acc1, acc2, 10, 100))
            t2 = threading.Thread(target=worker, args=(acc2, acc1, 10, 100))
            threads.extend([t1, t2])
            
        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
            
        self.assertEqual(1000.0, acc1.balance)
        self.assertEqual(1000.0, acc2.balance)

class TestBoundary(unittest.TestCase):
    """Boundary tests for edge cases."""
    
    def test_pin_reset_after_success(self):
        """Test PIN attempt counter resets after successful auth."""
        account = Account("ACC001", AccountType.CHECKING, 1000.0, "1234")
        
        # Two failed attempts
        account.validate_pin("0000")
        account.validate_pin("1111")
        
        # Successful attempt should reset counter
        self.assertTrue(account.validate_pin("1234"))
        
        # Two more failed attempts
        account.validate_pin("0000")
        account.validate_pin("1111")
        
        # Account should NOT be locked
        self.assertFalse(account.is_locked)
    
    def test_different_account_types(self):
        """Test different account types."""
        savings = Account("SAV001", AccountType.SAVINGS, 5000.0, "5678")
        self.assertEqual(AccountType.SAVINGS, savings.account_type)
        self.assertEqual(5000.0, savings.balance)


if __name__ == "__main__":
    # Run tests
    print("Running ATM System Tests...\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAccount))
    suite.addTests(loader.loadTestsFromTestCase(TestCard))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestConcurrent))
    suite.addTests(loader.loadTestsFromTestCase(TestBoundary))
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n=== Test Results ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
