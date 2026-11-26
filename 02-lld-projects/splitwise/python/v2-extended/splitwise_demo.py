"""
Demo for Splitwise - v1 Basic
"""
from user import User
from expense_manager import ExpenseManager
from split import SplitType


def main():
    """Run the Splitwise demo."""
    print("=" * 50)
    print("Splitwise Demo - v1 Basic")
    print("=" * 50)
    
    # Create expense manager
    manager = ExpenseManager()
    
    # Create users
    alice = User("U1", "Alice", "alice@email.com")
    bob = User("U2", "Bob", "bob@email.com")
    charlie = User("U3", "Charlie", "charlie@email.com")
    diana = User("U4", "Diana", "diana@email.com")
    
    manager.add_user(alice)
    manager.add_user(bob)
    manager.add_user(charlie)
    manager.add_user(diana)
    
    print("\n--- Users Added ---")
    print(f"  {alice}")
    print(f"  {bob}")
    print(f"  {charlie}")
    print(f"  {diana}")
    
    # Test 1: Equal split - Alice pays $100 for dinner, split among 4
    print("\n--- Test 1: Equal Split ---")
    print("Alice pays $100 for dinner, split equally among Alice, Bob, Charlie, Diana")
    
    expense1 = manager.add_expense(
        amount=100.0,
        description="Dinner",
        paid_by_id="U1",
        split_type=SplitType.EQUAL,
        participant_ids=["U1", "U2", "U3", "U4"]
    )
    
    if expense1:
        print(f"Created: {expense1}")
        print("Each person's share: $25.00")
    
    print("\nCurrent Balances:")
    manager.show_balances()
    
    # Test 2: Exact split - Bob pays $150, different amounts
    print("\n--- Test 2: Exact Split ---")
    print("Bob pays $150 for groceries: Alice-$40, Bob-$50, Charlie-$60")
    
    expense2 = manager.add_expense(
        amount=150.0,
        description="Groceries",
        paid_by_id="U2",
        split_type=SplitType.EXACT,
        participant_ids=["U1", "U2", "U3"],
        split_details=[40.0, 50.0, 60.0]
    )
    
    if expense2:
        print(f"Created: {expense2}")
    
    print("\nCurrent Balances:")
    manager.show_balances()
    
    # Test 3: Percentage split
    print("\n--- Test 3: Percentage Split ---")
    print("Charlie pays $200 for travel: Alice-25%, Charlie-50%, Diana-25%")
    
    expense3 = manager.add_expense(
        amount=200.0,
        description="Travel",
        paid_by_id="U3",
        split_type=SplitType.PERCENTAGE,
        participant_ids=["U1", "U3", "U4"],
        split_details=[25.0, 50.0, 25.0]
    )
    
    if expense3:
        print(f"Created: {expense3}")
    
    print("\n--- Final Balances ---")
    manager.show_balances()
    
    # Show individual balances
    print("\n--- Alice's Balances ---")
    manager.show_balances("U1")
    
    print("\n--- Bob's Balances ---")
    manager.show_balances("U2")


if __name__ == "__main__":
    main()
