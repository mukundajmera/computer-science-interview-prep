"""
Tests for Splitwise Python implementations.
"""
import unittest
import sys
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
HELPER_DIR = TEST_DIR.parents[2] / "test_helpers"
if str(HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(HELPER_DIR))

from imports import import_modules_from


SPLITWISE_MODULES = ["expense_manager", "expense", "split", "user", "group"]


def version_path(version: str) -> Path:
    return TEST_DIR.parent / version


class TestSplitwiseV1(unittest.TestCase):
    """Tests for v1 basic Splitwise implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        modules = import_modules_from(
            version_path("v1-basic"),
            ["user", "expense_manager", "split"],
            purge_modules=SPLITWISE_MODULES,
        )
        
        self.User = modules["user"].User
        self.ExpenseManager = modules["expense_manager"].ExpenseManager
        self.SplitType = modules["split"].SplitType
        
        self.manager = self.ExpenseManager()
        self.alice = self.User("U1", "Alice", "alice@email.com")
        self.bob = self.User("U2", "Bob", "bob@email.com")
        self.charlie = self.User("U3", "Charlie", "charlie@email.com")
        
        self.manager.add_user(self.alice)
        self.manager.add_user(self.bob)
        self.manager.add_user(self.charlie)
    
    def test_add_user(self):
        """Test adding users."""
        user = self.manager.get_user("U1")
        self.assertIsNotNone(user)
        self.assertEqual(user.name, "Alice")
    
    def test_equal_split(self):
        """Test equal split expense."""
        expense = self.manager.add_expense(
            amount=90.0,
            description="Dinner",
            paid_by_id="U1",
            split_type=self.SplitType.EQUAL,
            participant_ids=["U1", "U2", "U3"]
        )
        
        self.assertIsNotNone(expense)
        self.assertEqual(expense.amount, 90.0)
        
        # Bob and Charlie should each owe Alice $30
        bob_balance = self.manager.get_balance("U2")
        self.assertAlmostEqual(bob_balance.get("U1", 0), 30.0, places=2)
    
    def test_exact_split(self):
        """Test exact split expense."""
        expense = self.manager.add_expense(
            amount=100.0,
            description="Shopping",
            paid_by_id="U2",
            split_type=self.SplitType.EXACT,
            participant_ids=["U1", "U2", "U3"],
            split_details=[40.0, 35.0, 25.0]
        )
        
        self.assertIsNotNone(expense)
        
        alice_balance = self.manager.get_balance("U1")
        self.assertAlmostEqual(alice_balance.get("U2", 0), 40.0, places=2)
        
        charlie_balance = self.manager.get_balance("U3")
        self.assertAlmostEqual(charlie_balance.get("U2", 0), 25.0, places=2)
    
    def test_percentage_split(self):
        """Test percentage split expense."""
        expense = self.manager.add_expense(
            amount=100.0,
            description="Trip",
            paid_by_id="U3",
            split_type=self.SplitType.PERCENTAGE,
            participant_ids=["U1", "U2", "U3"],
            split_details=[50.0, 30.0, 20.0]
        )
        
        self.assertIsNotNone(expense)
        
        alice_balance = self.manager.get_balance("U1")
        self.assertAlmostEqual(alice_balance.get("U3", 0), 50.0, places=2)
    
    def test_invalid_exact_split(self):
        """Test that invalid exact split is rejected."""
        expense = self.manager.add_expense(
            amount=100.0,
            description="Invalid",
            paid_by_id="U1",
            split_type=self.SplitType.EXACT,
            participant_ids=["U1", "U2"],
            split_details=[60.0, 60.0]  # Total 120, not 100
        )
        
        self.assertIsNone(expense)
    
    def test_user_not_found(self):
        """Test expense with non-existent user."""
        expense = self.manager.add_expense(
            amount=100.0,
            description="Test",
            paid_by_id="U99",  # Non-existent
            split_type=self.SplitType.EQUAL,
            participant_ids=["U1", "U2"]
        )
        
        self.assertIsNone(expense)


class TestSplitwiseV2(unittest.TestCase):
    """Tests for v2 extended Splitwise implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        modules = import_modules_from(
            version_path("v2-extended"),
            ["expense_manager"],
            purge_modules=SPLITWISE_MODULES,
        )
        expense_manager = modules["expense_manager"]
        
        self.User = expense_manager.User
        self.ExpenseManager = expense_manager.ExpenseManager
        self.SplitType = expense_manager.SplitType
        
        self.manager = self.ExpenseManager()
        self.alice = self.User("U1", "Alice", "alice@email.com")
        self.bob = self.User("U2", "Bob", "bob@email.com")
        self.charlie = self.User("U3", "Charlie", "charlie@email.com")
        
        self.manager.add_user(self.alice)
        self.manager.add_user(self.bob)
        self.manager.add_user(self.charlie)
    
    def test_create_group(self):
        """Test group creation."""
        group = self.manager.create_group("Trip Group", "U1")
        
        self.assertIsNotNone(group)
        self.assertEqual(group.name, "Trip Group")
        self.assertIn(self.alice, group.members)
    
    def test_add_member_to_group(self):
        """Test adding members to group."""
        group = self.manager.create_group("Test Group", "U1")
        result = self.manager.add_member_to_group(group.group_id, "U2")
        
        self.assertTrue(result)
        self.assertIn(self.bob, group.members)
    
    def test_group_expense(self):
        """Test adding expense to a group."""
        group = self.manager.create_group("Dinner Group", "U1")
        self.manager.add_member_to_group(group.group_id, "U2")
        self.manager.add_member_to_group(group.group_id, "U3")
        
        expense = self.manager.add_expense(
            amount=90.0,
            description="Group Dinner",
            paid_by_id="U1",
            split_type=self.SplitType.EQUAL,
            participant_ids=["U1", "U2", "U3"],
            group_id=group.group_id
        )
        
        self.assertIsNotNone(expense)
        self.assertEqual(expense.group_id, group.group_id)
    
    def test_settlement_suggestions(self):
        """Test that settlement suggestions are generated."""
        # Add some expenses
        self.manager.add_expense(
            amount=90.0,
            description="Dinner",
            paid_by_id="U1",
            split_type=self.SplitType.EQUAL,
            participant_ids=["U1", "U2", "U3"]
        )
        
        settlements = self.manager.suggest_settlements()
        
        self.assertIsInstance(settlements, list)
        # Should have some settlements
        self.assertGreater(len(settlements), 0)


class TestSplitwiseV3(unittest.TestCase):
    """Tests for v3 optimized Splitwise implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        modules = import_modules_from(
            version_path("v3-optimized"),
            ["expense_manager"],
            purge_modules=SPLITWISE_MODULES,
        )
        expense_manager = modules["expense_manager"]
        
        self.User = expense_manager.User
        self.ExpenseManager = expense_manager.ExpenseManager
        self.SplitType = expense_manager.SplitType
        self.Currency = expense_manager.Currency
        
        self.manager = self.ExpenseManager()
        self.alice = self.User("U1", "Alice", "alice@email.com")
        self.bob = self.User("U2", "Bob", "bob@email.com")
        self.charlie = self.User("U3", "Charlie", "charlie@email.com")
        
        self.manager.add_user(self.alice)
        self.manager.add_user(self.bob)
        self.manager.add_user(self.charlie)
    
    def test_thread_safe_expense_addition(self):
        """Test concurrent expense addition."""
        import threading
        
        def add_expense(i):
            self.manager.add_expense(
                amount=100.0,
                description=f"Expense {i}",
                paid_by_id="U1",
                split_type=self.SplitType.EQUAL,
                participant_ids=["U1", "U2"]
            )
        
        threads = [threading.Thread(target=add_expense, args=(i,)) for i in range(5)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All expenses should be added without error
        # Check that balances are correct (5 expenses of $100 each, split equally)
        # Bob should owe Alice $50 * 5 = $250
        bob_balance = self.manager.get_balance("U2")
        self.assertAlmostEqual(bob_balance.get("U1", 0), 250.0, places=2)
    
    def test_record_payment(self):
        """Test recording settlement payments."""
        # Add an expense
        self.manager.add_expense(
            amount=100.0,
            description="Dinner",
            paid_by_id="U1",
            split_type=self.SplitType.EQUAL,
            participant_ids=["U1", "U2"]
        )
        
        # Bob owes Alice $50
        bob_balance = self.manager.get_balance("U2")
        self.assertAlmostEqual(bob_balance.get("U1", 0), 50.0, places=2)
        
        # Bob pays Alice $50
        result = self.manager.record_payment("U2", "U1", 50.0)
        self.assertTrue(result)
        
        # Balance should be zero now
        bob_balance = self.manager.get_balance("U2")
        self.assertAlmostEqual(bob_balance.get("U1", 0), 0.0, places=2)
    
    def test_optimized_settlements(self):
        """Test optimized settlement calculation."""
        # Create a chain of debts that can be simplified
        # A -> B -> C can become A -> C directly
        self.manager.add_expense(
            amount=100.0,
            description="Expense 1",
            paid_by_id="U2",
            split_type=self.SplitType.EXACT,
            participant_ids=["U1", "U2"],
            split_details=[100.0, 0.0]
        )
        
        self.manager.add_expense(
            amount=100.0,
            description="Expense 2",
            paid_by_id="U3",
            split_type=self.SplitType.EXACT,
            participant_ids=["U2", "U3"],
            split_details=[100.0, 0.0]
        )
        
        settlements = self.manager.get_simplified_settlements()
        
        # Should have at most 2 transactions
        self.assertLessEqual(len(settlements), 2)


if __name__ == '__main__':
    unittest.main()
